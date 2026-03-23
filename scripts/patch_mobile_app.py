import os
import re
import json

def patch_file(file_path, search_pattern, replacement, use_regex=False):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if use_regex:
        if re.search(search_pattern, content):
            new_content = re.sub(search_pattern, replacement, content)
            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Patched (Regex): {file_path}")
            else:
                 print(f"No changes (Same content): {file_path}")
        else:
            print(f"Pattern not found (Regex) in: {file_path}")
    else:
        if search_pattern in content:
            new_content = content.replace(search_pattern, replacement)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Patched: {file_path}")
        else:
            print(f"Pattern not found in: {file_path}")

def main():
    # -------------------------------------------------
    # 1. LOAD SETTINGS FROM JSON
    # -------------------------------------------------
    config_path = "app_config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        # Fallback if config is missing
        config = {
            "app_name": "Drop Down",
            "package_name": "com.dropdown.app",
            "local_url": "http://localhost:8000",
            "android_local_url": "http://10.0.2.2:8000",
            "prod_url": ""
        }

    APP_NAME = config.get("app_name", "Drop Down")
    LOCAL_URL = config.get("local_url", "http://localhost:8000")
    
    # --- AUTO-DETECT IP FOR REAL DEVICE TESTING ---
    PC_IP = "10.0.2.2" # Emulator fallback
    import socket
    try:
        # Get the real local IP (e.g. 192.168.x.x)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        PC_IP = s.getsockname()[0]
        s.close()
        print(f"Auto-Detected PC IP: {PC_IP}")
    except Exception:
        PC_IP = "10.0.2.2"

    ANDROID_LOCAL_URL = config.get("android_local_url", f"http://{PC_IP}:8000")
    PROD_URL = config.get("prod_url", "")
    PACKAGE_ID = config.get("package_name", "com.dropdown.app")
    
    BASE_DIR = os.getcwd()
    MOBILE_DIR = os.path.join(BASE_DIR, "mobile")
    
    if not os.path.exists(MOBILE_DIR):
        print("Mobile folder not found. Please run 'build_apps.bat' first.")
        return

    # -------------------------------------------------
    # 2. PATCH ANDROID (PACKAGE & NAME)
    # -------------------------------------------------
    # Manifest updates
    manifest_path = os.path.join(MOBILE_DIR, "android/app/src/main/AndroidManifest.xml")
    if os.path.exists(manifest_path):
        # Permissions
        permission = '<uses-permission android:name="android.permission.INTERNET" />'
        if permission not in open(manifest_path).read():
            patch_file(manifest_path, '<application', f'    {permission}\n    <application')
        
        # Cleartext traffic
        if 'android:usesCleartextTraffic="true"' not in open(manifest_path).read():
            patch_file(manifest_path, '<application', '<application\n        android:usesCleartextTraffic="true"')
        
        # App Label
        patch_file(manifest_path, 'android:label="mobile"', f'android:label="{APP_NAME}"')
        # Also handle potential platform-specific placeholders
        patch_file(manifest_path, 'android:label="Dropdown"', f'android:label="{APP_NAME}"')

    # Update build.gradle for package ID (v4+ style)
    gradle_path = os.path.join(MOBILE_DIR, "android/app/build.gradle")
    if os.path.exists(gradle_path):
        # Update applicationId
        patch_file(gradle_path, 'applicationId "com.example.mobile"', f'applicationId "{PACKAGE_ID}"', use_regex=False)
        # Update namespace for newer Flutter versions
        patch_file(gradle_path, 'namespace "com.example.mobile"', f'namespace "{PACKAGE_ID}"', use_regex=False)

    # -------------------------------------------------
    # 3. PATCH PUBSPEC.YAML
    # -------------------------------------------------
    pubspec_path = os.path.join(MOBILE_DIR, "pubspec.yaml")
    if os.path.exists(pubspec_path):
        patch_file(pubspec_path, 'name: mobile', f'name: {APP_NAME.lower().replace(" ", "_")}')
        patch_file(pubspec_path, 'description: "A new Flutter project."', f'description: "{APP_NAME} Mobile App"')

    # -------------------------------------------------
    # 4. PATCH LIB/MAIN.DART (UNIVERSAL WEBVIEW)
    # -------------------------------------------------
    main_dart_path = os.path.join(MOBILE_DIR, "lib/main.dart")
    
    # Decide which URL to use
    FINAL_URL = PROD_URL if PROD_URL and "your-production-url" not in PROD_URL else LOCAL_URL
    USE_PROD = 1 if (PROD_URL and "your-production-url" not in PROD_URL) else 0

    if os.path.exists(os.path.dirname(main_dart_path)):
        webview_code = f"""import 'dart:io' show Platform;
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {{
  // Ensure Flutter is initialized before running the app
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}}

class MyApp extends StatelessWidget {{
  const MyApp({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      title: '{APP_NAME}',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.dark,
          primary: Colors.blueAccent
        ),
        useMaterial3: true,
      ),
      home: const WebViewPage(),
    );
  }}
}}

class WebViewPage extends StatefulWidget {{
  const WebViewPage({{super.key}});

  @override
  State<WebViewPage> createState() => _WebViewPageState();
}}

class _WebViewPageState extends State<WebViewPage> {{
  late final WebViewController _controller;
  bool _isLoading = true;

  @override
  void initState() {{
    super.initState();
    
    // Determine the base URL
    String initialUrl = '{FINAL_URL}';
    
    // If not in production, use local IP for Android Emulator
    if ({USE_PROD} == 0) {{
        try {{
          if (Platform.isAndroid) {{
            initialUrl = '{ANDROID_LOCAL_URL}';
          }}
        }} catch (_) {{}}
    }}

    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0x00000000))
      ..setUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {{}},
          onPageStarted: (String url) => setState(() => _isLoading = true),
          onPageFinished: (String url) => setState(() => _isLoading = false),
          onWebResourceError: (WebResourceError error) {{
             debugPrint("Web error: ${{error.description}}");
          }},
        ),
      )
      ..loadRequest(Uri.parse(initialUrl));
  }}

  @override
  Widget build(BuildContext context) {{
    // Windows support check
    bool isWindows = false;
    try {{ isWindows = Platform.isWindows; }} catch(_) {{}}

    if (isWindows) {{
       return Scaffold(
         appBar: AppBar(title: const Text('{APP_NAME} Explorer')),
         body: Center(
           child: Column(
             mainAxisAlignment: MainAxisAlignment.center,
             children: [
               const Icon(Icons.desktop_windows, size: 64, color: Colors.blueAccent),
               const SizedBox(height: 16),
               const Text("Windows View mode enabled.", style: TextStyle(fontSize: 18)),
               const SizedBox(height: 10),
               const Text("Click below to open in your system browser:"),
               const SizedBox(height: 20),
               ElevatedButton.icon(
                 onPressed: () {{
                    // Note: Would use url_launcher here
                    debugPrint("URL launcher would open: {FINAL_URL}");
                 }}, 
                 icon: const Icon(Icons.open_in_browser),
                 label: const Text("Open App"),
               )
             ],
           ),
         ),
       );
    }}

    return Scaffold(
      appBar: AppBar(
        title: const Text('{APP_NAME}'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _controller.reload(),
          ),
        ],
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_isLoading)
            const Center(child: CircularProgressIndicator()),
        ],
      ),
    );
  }}
}}
"""
        with open(main_dart_path, "w", encoding="utf-8") as f:
            f.write(webview_code)
        print(f"Patched and Finalized: {main_dart_path}")

    print("\\nAPP SETTINGS APPLIED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

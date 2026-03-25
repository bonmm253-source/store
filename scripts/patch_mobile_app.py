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
            "prod_url": "https://drop-down-store.onrender.com"
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
    PROD_URL = config.get("prod_url", "https://drop-down-store.onrender.com")
    PACKAGE_ID = config.get("package_name", "com.dropdown.app")
    
    BASE_DIR = os.getcwd()
    MOBILE_DIR = os.path.join(BASE_DIR, "mobile")
    
    if not os.path.exists(MOBILE_DIR):
        print("Mobile folder not found. Please run 'build_apps.bat' or use docker to create the 'mobile' folder first.")
        return

    # -------------------------------------------------
    # 2. PATCH ANDROID (PACKAGE, NAME & PERMISSIONS)
    # -------------------------------------------------
    # Manifest updates
    manifest_path = os.path.join(MOBILE_DIR, "android/app/src/main/AndroidManifest.xml")
    if os.path.exists(manifest_path):
        # Permissions
        with open(manifest_path, "r") as f:
            manifest_content = f.read()

        permissions = [
            '<uses-permission android:name="android.permission.INTERNET" />',
            '<uses-permission android:name="android.permission.CAMERA" />',
            '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />',
            '<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />'
        ]
        
        for perm in permissions:
            if perm not in manifest_content:
                patch_file(manifest_path, '<application', f'    {perm}\n    <application')
        
        # Cleartext traffic
        if 'android:usesCleartextTraffic="true"' not in manifest_content:
            patch_file(manifest_path, '<application', '<application\n        android:usesCleartextTraffic="true"')
        
        # App Label
        patch_file(manifest_path, 'android:label="mobile"', f'android:label="{APP_NAME}"')
        patch_file(manifest_path, 'android:label="Dropdown"', f'android:label="{APP_NAME}"')

    # Update build.gradle for package ID
    gradle_path = os.path.join(MOBILE_DIR, "android/app/build.gradle")
    if os.path.exists(gradle_path):
        patch_file(gradle_path, 'applicationId "com.example.mobile"', f'applicationId "{PACKAGE_ID}"')
        patch_file(gradle_path, 'namespace "com.example.mobile"', f'namespace "{PACKAGE_ID}"')

    # -------------------------------------------------
    # 3. PATCH PUBSPEC.YAML
    # -------------------------------------------------
    pubspec_path = os.path.join(MOBILE_DIR, "pubspec.yaml")
    if os.path.exists(pubspec_path):
        patch_file(pubspec_path, 'name: mobile', f'name: {APP_NAME.lower().replace(" ", "_")}')
        patch_file(pubspec_path, 'description: "A new Flutter project."', f'description: "{APP_NAME} Mobile App"')
        
        # Add common dependencies if missing
        with open(pubspec_path, "r") as f:
            pubspec_content = f.read()
            
        if 'flutter_launcher_icons:' not in pubspec_content:
            patch_file(pubspec_path, 'dev_dependencies:', 'dev_dependencies:\n  flutter_launcher_icons: ^0.13.1')
        
        # Add icon config if missing
        icon_config = """
flutter_launcher_icons:
  android: true
  ios: true
  image_path: "../assets/logo.png"
  min_sdk_android: 21
"""
        if 'flutter_launcher_icons:' not in pubspec_content:
            with open(pubspec_path, "a") as f:
                f.write(icon_config)

    # -------------------------------------------------
    # 4. PATCH LIB/MAIN.DART (UNIVERSAL WEBVIEW)
    # -------------------------------------------------
    main_dart_path = os.path.join(MOBILE_DIR, "lib/main.dart")
    
    # Decide which URL to use
    FINAL_URL = PROD_URL if (PROD_URL and "onrender.com" in PROD_URL) else LOCAL_URL
    USE_PROD = 1 if ("onrender.com" in FINAL_URL) else 0

    webview_code = f"""import 'dart:io' show Platform;
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:url_launcher/url_launcher.dart';

void main() {{
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
          brightness: Brightness.light,
          primary: const Color(0xFF673AB7),
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: Colors.deepPurple,
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
  double _progress = 0;
  bool _hasError = false;

  @override
  void initState() {{
    super.initState();
    
    String initialUrl = '{FINAL_URL}';
    
    if ({USE_PROD} == 0) {{
        try {{
          if (Platform.isAndroid) {{
            initialUrl = '{ANDROID_LOCAL_URL}';
          }}
        }} catch (_) {{}}
    }}

    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(Colors.white)
      ..setUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1")
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {{
            setState(() {{
              _progress = progress / 100.0;
            }});
          }},
          onPageStarted: (String url) => setState(() => _isLoading = true),
          onPageFinished: (String url) => setState(() => _isLoading = false),
          onWebResourceError: (WebResourceError error) {{
             debugPrint("Web error: ${{error.description}}");
             if (error.isForMainFrame ?? true) {{
                setState(() => _hasError = true);
             }}
          }},
          onNavigationRequest: (NavigationRequest request) {{
            if (request.url.startsWith('https://www.youtube.com/')) {{
              return NavigationDecision.prevent;
            }}
            return NavigationDecision.navigate;
          }},
        ),
      )
      ..loadRequest(Uri.parse(initialUrl));
  }}

  Future<void> _refresh() async {{
    setState(() {{
      _hasError = false;
    }});
    await _controller.reload();
  }}

  @override
  Widget build(BuildContext context) {{
    bool isMobile = false;
    try {{ isMobile = Platform.isAndroid || Platform.isIOS; }} catch(_) {{}}

    if (!isMobile) {{
       // Windows / Linux / macOS placeholder with better UI
       return Scaffold(
         appBar: AppBar(
           title: const Text('{APP_NAME} Desktop'),
           backgroundColor: Colors.deepPurple,
           foregroundColor: Colors.white,
         ),
         body: Center(
           child: Container(
             constraints: const BoxConstraints(maxWidth: 400),
             padding: const EdgeInsets.all(32),
             child: Column(
               mainAxisAlignment: MainAxisAlignment.center,
               children: [
                 const Icon(Icons.shop_two_outlined, size: 80, color: Colors.deepPurple),
                 const SizedBox(height: 24),
                 Text(
                   "{APP_NAME}",
                   style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                 ),
                 const SizedBox(height: 12),
                 const Text(
                   "This is the desktop version of the Drop Down Store App.",
                   textAlign: TextAlign.center,
                   style: TextStyle(fontSize: 16, color: Colors.grey),
                 ),
                 const SizedBox(height: 32),
                 SizedBox(
                   width: double.infinity,
                   child: ElevatedButton.icon(
                     onPressed: () async {{
                        final url = Uri.parse('{FINAL_URL}');
                        if (await canLaunchUrl(url)) {{
                          await launchUrl(url, mode: LaunchMode.externalApplication);
                        }}
                     }}, 
                     icon: const Icon(Icons.open_in_browser),
                     label: const Text("LAUNCH STORE IN BROWSER"),
                     style: ElevatedButton.styleFrom(
                       padding: const EdgeInsets.symmetric(vertical: 16),
                       backgroundColor: Colors.deepPurple,
                       foregroundColor: Colors.white,
                     ),
                   ),
                 ),
                 const SizedBox(height: 16),
                 const Text("Note: Native WebView for Windows coming soon.", style: TextStyle(fontSize: 12, color: Colors.grey))
               ],
             ),
           ),
         ),
       );
    }}

    return Scaffold(
      appBar: AppBar(
        title: const Text('{APP_NAME}'),
        centerTitle: true,
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refresh,
          ),
        ],
      ),
      body: _hasError 
        ? Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.wifi_off, size: 60, color: Colors.grey),
                const SizedBox(height: 16),
                const Text("Unable to connect to the store."),
                const SizedBox(height: 20),
                ElevatedButton(onPressed: _refresh, child: const Text("Retry"))
              ],
            ),
          )
        : Column(
            children: [
              if (_isLoading)
                LinearProgressIndicator(value: _progress, color: Colors.orange),
              Expanded(
                child: RefreshIndicator(
                  onRefresh: _refresh,
                  child: WebViewWidget(controller: _controller),
                ),
              ),
            ],
          ),
      bottomNavigationBar: isMobile ? NavigationBar(
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: "Home"),
          NavigationDestination(icon: Icon(Icons.shopping_cart), label: "Cart"),
          NavigationDestination(icon: Icon(Icons.person), label: "Profile"),
        ],
        onDestinationSelected: (idx) {{
           if (idx == 0) _controller.loadRequest(Uri.parse('{FINAL_URL}'));
           if (idx == 1) _controller.loadRequest(Uri.parse('{FINAL_URL}/cart/'));
           if (idx == 2) _controller.loadRequest(Uri.parse('{FINAL_URL}/profile/'));
        }},
      ) : null,
    );
  }}
}}
"""
    with open(main_dart_path, "w", encoding="utf-8") as f:
        f.write(webview_code)
    print(f"Patched and Finalized: {main_dart_path}")

    print("\nAPP SETTINGS APPLIED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

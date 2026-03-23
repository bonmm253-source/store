import os
path = 'templates/cart.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '{% block scripts %}' in line:
        new_lines.append('{% endblock %}\n')
        new_lines.append(line)
    elif '                            item.product.discount_price|default:item.product.price }}</div>' in line:
        continue
    elif 'Qty: {{ item.quantity }} x ${{ ' in line or 'Qty: {{ item.quantity }} x ${{' in line:
        new_lines.append('                        <div style="color: var(--jumia-light-text); font-size: 12px;">Qty: {{ item.quantity }} x ${{ item.product.discount_price|default:item.product.price }}</div>\n')
    elif 'CHECKOUT (${{ cart.total_price' in line:
        new_lines.append('        <a href="{% url \'pay\' %}" class="btn-primary" style="text-decoration: none;">CHECKOUT (${{ cart.total_price }})</a>\n')
    elif '            }})</a>' in line:
        continue
    elif '{% endblock %}' in line and i == len(lines) - 1:
        pass # Skip the last endblock
    elif '{% endblock %}' in line and i == len(lines) - 2:
        new_lines.append(line) # keep the scripts endblock
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done modifying cart.html')

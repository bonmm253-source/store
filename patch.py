import os
path = 'templates/catalog_list.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('${{\n                shoe.discount_price|default:shoe.price }}', '${{ shoe.discount_price|default:shoe.price }}')
content = content.replace('${{\r\n                shoe.discount_price|default:shoe.price }}', '${{ shoe.discount_price|default:shoe.price }}')

content = content.replace('${{\n                watch.discount_price|default:watch.price }}', '${{ watch.discount_price|default:watch.price }}')
content = content.replace('${{\r\n                watch.discount_price|default:watch.price }}', '${{ watch.discount_price|default:watch.price }}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done modifying catalog_list.html')

from albam.engines.mtfw.arc_fs import MTFW_FS
from tests.mtfw.scripts.catalog_paths import hash_virtual_path
import json
game_fs = MTFW_FS(r'C:\Program Files (x86)\Steam\steamapps\common\Resident Evil 5')
out = []
for p in sorted(game_fs.walk.files()):
    if p.lower().endswith('.lot'):
        out.append({'app_id': 're5', 'lot_path_hash': hash_virtual_path(p)})
with open('lot_parsing_hashes.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=4)
print(f'written {len(out)} LOT hashes')

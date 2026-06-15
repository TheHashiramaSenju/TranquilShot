# TranquilShot — Simulation Asset Manifest Notes

## Project overview
Autonomous elephant tranquilizer drone simulation.
The Gazebo sim must demonstrate autonomous target detection, multi-gate sensor fusion,
nearest-target arbitration, and precision targeting. Every asset must serve one of
those four functions or enrich the believability of the demo environment.

## Asset priority order
1. ELEPH_001 — primary target, must be high quality, realistic scale
2. DRONE_001 — the vehicle the audience watches, must look credible
3. ENV_001 — terrain, sets the entire scene tone
4. Everything else — scene dressing, adds depth

## Scale reference (critical)
- African elephant adult: ~5–6m long, 2.5–3.2m tall, 1.5–2m wide
- DJI-class heavy lift drone: ~0.6–0.8m wheelbase, ~0.15–0.2m height
- Camera gimbal: ~0.07–0.1m cube
- Dart launcher tube: ~0.1–0.15m long, ~0.04m diameter
- All assets MUST be in meters. Z-up. Right-hand coordinate system.

## Mesh quality guidelines
- Visual mesh: no upper poly limit but keep reasonable (under 100K tris per asset)
- Collision mesh: simplified, convex, under 2K tris
- Textures: 1024×1024 minimum, 2048×2048 preferred, PNG format
- Maps: albedo/base_color required, roughness preferred, normal optional

## Coordinate system
- All assets: Z-up, meters, right-hand
- If your asset comes in Y-up or inches, note it in metadata.json and I will handle conversion

## Naming convention
- Files: lowercase_underscore.dae, lowercase_underscore.png
- No spaces, no special characters in any filename

## License discipline
- Record source URL and license for every asset
- Accepted licenses: CC0, CC BY, CC BY-SA, MIT
- Not accepted for this project: CC BY-NC, CC BY-ND, commercial-only assets
- If you own/created the asset: write "original" in source_url

## Status codes for asset_manifest.csv quality_rating column
- empty: not filled yet
- 1: rough placeholder
- 2: acceptable
- 3: good
- 4: presentation-ready
- 5: excellent/hero quality

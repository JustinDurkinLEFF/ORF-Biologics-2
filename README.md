# ORF Bio — v10 (v9 structure × colour-field system)

v9's pages, copy, logos, fonts and images, restyled with the colour-field system from the previous rebuild.
Nine pages: index, therapeutics, pipeline, services, news, about, registry, contact, distributors.

## Preview
Drag the `dist` folder (or the site zip) onto https://app.netlify.com/drop. Pages open locally too:
header and footer are baked into each page instead of fetched at runtime.

**Fonts:** Gibson loads from the v9 Adobe Fonts kit (`idg1sih`). Adobe kits are domain-locked,
so add the Netlify preview domain in the kit's settings or the site falls back to the system sans.

## Edit + rebuild
`python3 build.py` → writes `dist/` from `src/pages`, `src/css/orf.css`, `src/js/orf.js`, `src/images`.

## Changes

### Round 2 (11 Sep)
- Global: nav is always the dark pill with the white logo (keeps its own colours while the page morphs).
- Home: stock image band removed. What-sets-us-apart views are now 4:3 (shorter); step spacing unchanged.
  Signature Therapeutics tile is an image placeholder. Registry segment restored to the previous full yellow
  shift with its original copy and dot field.
- Therapeutics: accordion art replaced with image placeholders; pending areas tagged "In development"
  (About's hub diagram says the same, for consistency).
- News: same card layout as the home "Latest News & Events"; feature image is Keegan's v9 photo.
- Registry: image placeholders above Genomic data, Tissue, Blood samples.
- Distributors: rebuilt to the v9 reference: region tabs in a row, distributor links below. In the main nav (after Registry) and footer.

### Round 1
- v9 structure, copy, logos, Gibson; colour-field system from the previous rebuild.
- Hero: particles + stacked title in Gibson, softer bottom radius, scroll progress line removed.
- Sticky "views" with image placeholders; Our Story full-width interruptor; Pipeline strands animation kept.
- News tags removed; footer CTA struck, Contact Us button in the footer; page headers shortened; "Next" links removed.
- Pipeline: "Programs by stage" tracker with v9 program data.

**Image placeholders:** every slot uses the same component. Drop an `<img src="images/…" alt="">` into the
host element (`.view`, `.tile`, `.area__art`, `.sample__media`) and it covers the placeholder.

## Open items (search `⚠`, `data-todo`, `.flag`, `.todo`)
- Image placeholders: home views ×4 (4:3) + Signature Therapeutics (5:4); therapeutics ×5 (16:10); registry ×3 (16:10).
- News feature image is an Unsplash hotlink from v9 — download it into `images/` before launch.
- Pipeline program names/stages are v9 placeholders (flagged on page).
- Therapeutics: Infectious + Metabolic disease copy ("Need info").
- About: registry launch MONTH; leadership/advisor headshots (monogram placeholders).
- News: no article pages yet; NORD registration URL.
- Contact form posts to `#` — wire to the WordPress form plugin.
- Distributors: Japan (Aoba Corporation) has no URL. Privacy Policy URL.
- Registry page legend "1 dot = 1 million people" is new copy — delete if content must stay strictly v9.
- Therapeutics "In development" tags are a status claim; confirm with the client.
- Not carried over: v9 Theme A/B demo toggle, hero stock video.

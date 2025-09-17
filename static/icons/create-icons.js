// Simple icon generator - creates a fitness-themed icon
const fs = require('fs');
const path = require('path');

// Simple SVG template for fitness app icon
const svgTemplate = `
<svg width="{size}" height="{size}" viewBox="0 0 192 192" xmlns="http://www.w3.org/2000/svg">
  <rect width="192" height="192" rx="32" fill="#10b981"/>
  <g transform="translate(96, 96)">
    <!-- Heart/Love for fitness -->
    <path d="M-24,-10 C-24,-20 -16,-28 -6,-28 C4,-28 12,-20 12,-10 L12,10 L12,10 C12,20 4,28 -6,28 C-16,28 -24,20 -24,10 Z"
          fill="white" transform="translate(0, -20)"/>
    <!-- Dumbbell -->
    <rect x="-30" y="10" width="60" height="8" rx="4" fill="white"/>
    <rect x="-35" y="5" width="8" height="18" rx="4" fill="white"/>
    <rect x="27" y="5" width="8" height="18" rx="4" fill="white"/>
  </g>
</svg>
`;

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];

console.log('Creating app icons...');

sizes.forEach(size => {
  const svg = svgTemplate.replace(/{size}/g, size);
  const filename = `icon-${size}x${size}.svg`;
  const filepath = path.join(__dirname, filename);

  fs.writeFileSync(filepath, svg);
  console.log(`Created ${filename}`);
});

console.log('Icons created successfully!');
console.log('Note: For production, you should convert these SVGs to PNG format');
console.log('You can use tools like ImageMagick: convert icon-192x192.svg icon-192x192.png');
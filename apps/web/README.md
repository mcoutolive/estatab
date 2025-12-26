# estatab Web Frontend

Next.js + TypeScript + Bootstrap frontend for the estatab experimentation platform.

## Overview

Corporate-grade web interface for configuring, executing, and analyzing A/B/n experiments with:

- Professional, formal Portuguese language
- Responsive Bootstrap design
- localStorage persistence
- Real-time API integration

## Pages

### `/` - Home

Landing page with platform overview and CTA to create experiments.

### `/experiments/new` - Configuration

Form to configure experiment parameters:

- Metric name and type
- Hypothesis direction
- Methodology (fixed vs sequential)
- Significance level
- Multiple comparison correction
- Sequential testing parameters (conditional)

### `/experiments/run` - Data Input

Interface to add variants with their statistics:

- Variant name
- Sample size
- Mean/rate and standard deviation
- Control designation

### `/experiments/results` - Results Dashboard

Comprehensive results display:

- Summary cards (conclusion, alpha, methodology)
- Comparisons table with test statistics
- Sequential testing information
- Effect size visualization

## Development

### Local Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Build

```bash
# Type check
npm run type-check

# Build production bundle
npm run build

# Start production server
npm start
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - API endpoint (default: `http://localhost:8000`)

## Project Structure

```
apps/web/
├── app/
│   ├── experiments/
│   │   ├── new/page.tsx       # Configuration form
│   │   ├── run/page.tsx       # Data input
│   │   └── results/page.tsx   # Results dashboard
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Home page
│   └── globals.css            # Global styles
├── utils/
│   ├── ux.ts                  # UX dictionary
│   ├── types.ts               # TypeScript types
│   └── storage.ts             # localStorage utilities
└── package.json
```

## UX Dictionary

All user-facing text is centralized in `utils/ux.ts` for:

- Consistency across the platform
- Easy localization
- Professional corporate language
- Tooltips and help text

## Design Principles

- **Corporate aesthetics**: Professional color palette (blue, gray, white)
- **Formal language**: No emojis, slang, or informal tone
- **Responsive**: Mobile-first Bootstrap grid
- **Accessible**: Semantic HTML and ARIA labels
- **Auditable**: Clear display of all statistical metrics

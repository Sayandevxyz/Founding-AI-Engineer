"""Code Generation Agent: Produces an independent React TypeScript project with Tailwind CSS."""
import os
import json
from typing import Dict, Any, List
from backend.app.schemas.website_spec import WebsiteSpec
from backend.app.services.llm_provider import LLMProvider


class GeneratorAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def generate_project(self, spec: WebsiteSpec, project_dir: str) -> List[str]:
        """
        Generate complete standalone React TypeScript Vite project files.
        Returns a list of created relative file paths.
        """
        os.makedirs(os.path.join(project_dir, "src", "components"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "public", "assets"), exist_ok=True)

        created_files: List[str] = []

        # 1. package.json
        pkg_json = self._build_package_json(spec.title)
        self._write_file(project_dir, "package.json", pkg_json)
        created_files.append("package.json")

        # 2. tsconfig.json
        tsconfig = self._build_tsconfig()
        self._write_file(project_dir, "tsconfig.json", tsconfig)
        created_files.append("tsconfig.json")

        # 3. vite.config.ts
        vite_cfg = self._build_vite_config()
        self._write_file(project_dir, "vite.config.ts", vite_cfg)
        created_files.append("vite.config.ts")

        # 4. tailwind.config.js & postcss.config.js
        tailwind_cfg = self._build_tailwind_config(spec)
        self._write_file(project_dir, "tailwind.config.js", tailwind_cfg)
        created_files.append("tailwind.config.js")

        postcss_cfg = self._build_postcss_config()
        self._write_file(project_dir, "postcss.config.js", postcss_cfg)
        created_files.append("postcss.config.js")

        # 5. index.html
        index_html = self._build_index_html(spec)
        self._write_file(project_dir, "index.html", index_html)
        created_files.append("index.html")

        # 6. src/index.css
        index_css = self._build_index_css(spec)
        self._write_file(project_dir, "src/index.css", index_css)
        created_files.append("src/index.css")

        # 7. src/main.tsx
        main_tsx = self._build_main_tsx()
        self._write_file(project_dir, "src/main.tsx", main_tsx)
        created_files.append("src/main.tsx")

        # 8. src/components/Navbar.tsx
        navbar_code = self._build_navbar_component(spec)
        self._write_file(project_dir, "src/components/Navbar.tsx", navbar_code)
        created_files.append("src/components/Navbar.tsx")

        # 9. src/components/Hero.tsx
        hero_code = self._build_hero_component(spec)
        self._write_file(project_dir, "src/components/Hero.tsx", hero_code)
        created_files.append("src/components/Hero.tsx")

        # 10. src/components/Features.tsx
        features_code = self._build_features_component(spec)
        self._write_file(project_dir, "src/components/Features.tsx", features_code)
        created_files.append("src/components/Features.tsx")

        # 11. src/components/Testimonials.tsx
        testimonials_code = self._build_testimonials_component(spec)
        self._write_file(project_dir, "src/components/Testimonials.tsx", testimonials_code)
        created_files.append("src/components/Testimonials.tsx")

        # 12. src/components/CTA.tsx
        cta_code = self._build_cta_component(spec)
        self._write_file(project_dir, "src/components/CTA.tsx", cta_code)
        created_files.append("src/components/CTA.tsx")

        # 13. src/components/Footer.tsx
        footer_code = self._build_footer_component(spec)
        self._write_file(project_dir, "src/components/Footer.tsx", footer_code)
        created_files.append("src/components/Footer.tsx")

        # 14. src/App.tsx
        app_code = self._build_app_tsx(spec)
        self._write_file(project_dir, "src/App.tsx", app_code)
        created_files.append("src/App.tsx")

        # 15. README.md
        readme = self._build_project_readme(spec)
        self._write_file(project_dir, "README.md", readme)
        created_files.append("README.md")

        return created_files

    def _write_file(self, project_dir: str, rel_path: str, content: str):
        full_path = os.path.join(project_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _build_package_json(self, title: str) -> str:
        clean_name = title.lower().replace(" ", "-")[:30] or "reconstructed-app"
        return json.dumps({
            "name": clean_name,
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "lucide-react": "^0.453.0",
                "clsx": "^2.1.1",
                "tailwind-merge": "^2.5.4"
            },
            "devDependencies": {
                "@types/react": "^18.3.11",
                "@types/react-dom": "^18.3.1",
                "@vitejs/plugin-react": "^4.3.3",
                "typescript": "^5.6.3",
                "vite": "^5.4.9",
                "tailwindcss": "^3.4.14",
                "postcss": "^8.4.47",
                "autoprefixer": "^10.4.20"
            }
        }, indent=2)

    def _build_tsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": False,
                "noUnusedLocals": False,
                "noUnusedParameters": False,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"]
        }, indent=2)

    def _build_vite_config(self) -> str:
        return """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    cors: true,
  },
  preview: {
    host: '0.0.0.0',
    cors: true,
  }
});
"""

    def _build_tailwind_config(self, spec: WebsiteSpec) -> str:
        theme = spec.theme
        glob_pat = "./src/**/*.{js,ts,jsx,tsx}"
        return f"""/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [
    "./index.html",
    "{glob_pat}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          DEFAULT: '{theme.primaryColor}',
          hover: '{theme.secondaryColor}',
        }},
        accent: '{theme.accentColor}',
        brandBg: '{theme.backgroundColor}',
        brandText: '{theme.textColor}',
      }},
      fontFamily: {{
        sans: ['{theme.fontFamily.split(",")[0].strip()}', 'sans-serif'],
      }},
      borderRadius: {{
        brand: '{theme.borderRadius}',
      }}
    }},
  }},
  plugins: [],
}}
"""

    def _build_postcss_config(self) -> str:
        return """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

    def _build_index_html(self, spec: WebsiteSpec) -> str:
        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{spec.title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body class="bg-brandBg text-brandText antialiased selection:bg-primary selection:text-white">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

    def _build_index_css(self, spec: WebsiteSpec) -> str:
        theme = spec.theme
        return f"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --primary-color: {theme.primaryColor};
  --secondary-color: {theme.secondaryColor};
  --bg-color: {theme.backgroundColor};
  --text-color: {theme.textColor};
  font-family: {theme.fontFamily};
}}

html {{
  scroll-behavior: smooth;
}}

body {{
  background-color: var(--bg-color);
  color: var(--text-color);
  overflow-x: hidden;
}}
"""

    def _build_main_tsx(self) -> str:
        return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
"""

    def _build_navbar_component(self, spec: WebsiteSpec) -> str:
        nav = spec.navigation
        brand = nav.brandName or spec.title.split("-")[0].strip() or "Replicate.AI"
        cta_label = nav.cta.label if nav.cta else "Get Started"

        items_jsx = "\n".join([
            f'            <a href="{it.href}" className="text-sm font-medium text-slate-600 hover:text-primary transition-colors">{it.label}</a>'
            for it in nav.items
        ])
        mobile_items_jsx = "\n".join([
            f'            <a href="{it.href}" onClick={{() => setIsOpen(false)}} className="block py-2 text-base font-medium text-slate-700 hover:text-primary">{it.label}</a>'
            for it in nav.items
        ])

        return f"""import React, {{ useState }} from 'react';
import {{ Menu, X, ArrowRight }} from 'lucide-react';

export default function Navbar() {{
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/80 backdrop-blur-md transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-brand bg-primary flex items-center justify-center text-white font-bold shadow-md shadow-primary/20">
              {brand[:2].upper()}
            </div>
            <span className="font-bold text-lg text-slate-900 tracking-tight">{brand}</span>
          </div>

          <nav className="hidden md:flex items-center gap-8">
{items_jsx}
          </nav>

          <div className="hidden md:flex items-center gap-4">
            <a
              href="#cta"
              className="inline-flex items-center justify-center px-4 py-2 text-sm font-semibold text-white bg-primary hover:bg-primary-hover rounded-brand shadow-sm transition-all hover:scale-105 active:scale-95"
            >
              {cta_label}
              <ArrowRight className="ml-1.5 h-4 w-4" />
            </a>
          </div>

          <div className="flex md:hidden">
            <button
              type="button"
              onClick={{() => setIsOpen(!isOpen)}}
              className="text-slate-600 hover:text-slate-900 p-2 focus:outline-none"
              aria-label="Toggle menu"
            >
              {{isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}}
            </button>
          </div>
        </div>
      </div>

      {{isOpen && (
        <div className="md:hidden border-b border-slate-200 bg-white px-4 pt-2 pb-6 space-y-3">
{mobile_items_jsx}
          <div className="pt-2">
            <a
              href="#cta"
              onClick={{() => setIsOpen(false)}}
              className="w-full inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-primary rounded-brand"
            >
              {cta_label}
            </a>
          </div>
        </div>
      )}}
    </header>
  );
}}
"""

    def _build_hero_component(self, spec: WebsiteSpec) -> str:
        hero_sec = next((s for s in spec.sections if s.type == "hero"), None)
        heading = hero_sec.heading if hero_sec and hero_sec.heading else spec.title
        subheading = hero_sec.subheading if hero_sec and hero_sec.subheading else "An intelligent, high-velocity frontend architecture reconstructed with precision."
        btn_primary = hero_sec.buttons[0].label if hero_sec and hero_sec.buttons else "Start Free Today"
        btn_secondary = hero_sec.buttons[1].label if hero_sec and len(hero_sec.buttons) > 1 else "Watch Demo"

        hero_img_src = "/assets/hero-visual.svg"
        if spec.assets:
            hero_img_src = spec.assets[0].localPath

        return f"""import React from 'react';
import {{ ArrowRight, CheckCircle2, Play }} from 'lucide-react';

export default function Hero() {{
  return (
    <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28 bg-gradient-to-b from-slate-50 to-white border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
              <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
              Autonomous Next-Gen Platform
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 leading-[1.15]">
              {heading}
            </h1>

            <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto lg:mx-0 leading-relaxed font-normal">
              {subheading}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
              <a
                href="#cta"
                className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 text-base font-semibold text-white bg-primary hover:bg-primary-hover rounded-brand shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5"
              >
                {btn_primary}
                <ArrowRight className="ml-2 h-5 w-5" />
              </a>
              <a
                href="#features"
                className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 text-base font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 rounded-brand shadow-sm transition-all"
              >
                <Play className="mr-2 h-4 w-4 text-slate-500 fill-slate-500" />
                {btn_secondary}
              </a>
            </div>

            <div className="pt-4 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-xs text-slate-500 font-medium">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <span>Zero configuration required</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <span>Real-time validated build</span>
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                <span>100% independent React code</span>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 relative">
            <div className="relative mx-auto max-w-md lg:max-w-none rounded-2xl bg-gradient-to-tr from-primary/20 to-accent/20 p-2 shadow-2xl">
              <div className="overflow-hidden rounded-xl bg-slate-900 border border-slate-800 shadow-inner">
                <img
                  src="{hero_img_src}"
                  alt="Showcase Visual"
                  className="w-full h-auto object-cover max-h-[460px] transform transition-transform hover:scale-105 duration-700"
                  onError={{(e) => {{
                    // Fallback to SVG placeholder if file is not directly readable
                    (e.target as HTMLElement).setAttribute('src', '/assets/hero-visual.svg');
                  }}}}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}}
"""

    def _build_features_component(self, spec: WebsiteSpec) -> str:
        feat_sec = next((s for s in spec.sections if s.type == "features"), None)
        heading = feat_sec.heading if feat_sec and feat_sec.heading else "Engineered for Velocity and Scale"
        subheading = feat_sec.subheading if feat_sec and feat_sec.subheading else "Every component is designed from first principles to ensure peak user experience."

        items = feat_sec.items if feat_sec and feat_sec.items else [
            {"title": "Intelligent Automation", "description": "Streamline complex workflows with intelligent real-time processing and proactive checks.", "icon": "Zap"},
            {"title": "Seamless Integration", "description": "Connect instantly with your existing toolchains, databases, and continuous delivery pipelines.", "icon": "Layers"},
            {"title": "Enterprise Security", "description": "Bank-grade data isolation, encrypted channels, and fine-grained access governance out of the box.", "icon": "Shield"},
            {"title": "Deep Observability", "description": "Real-time metrics, telemetry graphs, and proactive anomaly detection for peak reliability.", "icon": "Activity"},
        ]

        cards_jsx = []
        icons_list = ["Zap", "Layers", "Shield", "Activity", "Code2", "Sparkles"]
        for idx, it in enumerate(items):
            icon_name = icons_list[idx % len(icons_list)]
            title = it.get("title") if isinstance(it, dict) else getattr(it, "title", None)
            desc = it.get("description") if isinstance(it, dict) else getattr(it, "description", None)
            title = title or f"Core Pillar {idx + 1}"
            desc = desc or "Optimized for enterprise workloads, continuous availability, and responsive interaction."
            cards_jsx.append(f"""          <div className="relative p-8 rounded-brand bg-white border border-slate-200/80 shadow-sm hover:shadow-md transition-all hover:-translate-y-1 group">
            <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform">
              <span className="font-bold text-lg">{idx + 1}</span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">{title}</h3>
            <p className="text-sm text-slate-600 leading-relaxed">{desc}</p>
          </div>""")

        all_cards = "\n".join(cards_jsx)

        return f"""import React from 'react';

export default function Features() {{
  return (
    <section id="features" className="py-20 bg-slate-50/60 border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-widest text-primary">Core Capabilities</h2>
          <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">{heading}</p>
          <p className="text-base sm:text-lg text-slate-600">{subheading}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
{all_cards}
        </div>
      </div>
    </section>
  );
}}
"""

    def _build_testimonials_component(self, spec: WebsiteSpec) -> str:
        test_sec = next((s for s in spec.sections if s.type == "testimonials"), None)
        heading = test_sec.heading if test_sec and test_sec.heading else "Loved by Leading Teams Worldwide"
        subheading = test_sec.subheading if test_sec and test_sec.subheading else "Discover why innovative leaders choose this platform."

        items = test_sec.items if test_sec and test_sec.items else [
            {"title": "Alex Vance", "role": "VP of Technology, ApexLabs", "description": "Replicate.AI eliminated weeks of repetitive frontend reconstruction. The generated code quality is phenomenal."},
            {"title": "Sarah Chen", "role": "Lead Architect, CloudMatrix", "description": "The ability to customize with natural language and see real-time validated rebuilds is revolutionary."},
            {"title": "Marcus Brody", "role": "Founder, HyperScale", "description": "We ported three legacy applications to modern React in a single afternoon. A huge competitive advantage."}
        ]

        cards_jsx = []
        for it in items:
            name = it.get("title") if isinstance(it, dict) else getattr(it, "title", None)
            role = it.get("role") if isinstance(it, dict) else getattr(it, "role", None)
            quote = it.get("description") if isinstance(it, dict) else getattr(it, "description", None)
            name = name or "Satisfied Customer"
            role = role or "Engineering Director"
            quote = quote or "Exceptional quality, speed, and developer experience."
            cards_jsx.append(f"""          <div className="bg-white p-8 rounded-brand border border-slate-200/80 shadow-sm flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex text-amber-400 gap-1 text-sm font-bold">
                ★★★★★
              </div>
              <p className="text-slate-700 text-sm leading-relaxed italic">"{quote}"</p>
            </div>
            <div className="pt-6 mt-6 border-t border-slate-100 flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-700 text-sm">
                {name[:1]}
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-900">{name}</h4>
                <p className="text-xs text-slate-500">{role}</p>
              </div>
            </div>
          </div>""")

        all_cards = "\n".join(cards_jsx)

        return f"""import React from 'react';

export default function Testimonials() {{
  return (
    <section className="py-20 bg-white border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-3">
          <p className="text-xs font-bold uppercase tracking-widest text-primary">Testimonials</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">{heading}</h2>
          <p className="text-slate-600 text-base">{subheading}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
{all_cards}
        </div>
      </div>
    </section>
  );
}}
"""

    def _build_cta_component(self, spec: WebsiteSpec) -> str:
        cta_sec = next((s for s in spec.sections if s.type == "cta"), None)
        heading = cta_sec.heading if cta_sec and cta_sec.heading else "Ready to Experience the Future?"
        subheading = cta_sec.subheading if cta_sec and cta_sec.subheading else "Launch your reconstructed application today with instant preview and AI editing."

        return f"""import React from 'react';
import {{ ArrowRight, ShieldCheck }} from 'lucide-react';

export default function CTA() {{
  return (
    <section id="cta" className="py-20 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white relative overflow-hidden">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10 space-y-6">
        <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight">
          {heading}
        </h2>
        <p className="text-lg text-slate-300 max-w-2xl mx-auto font-normal">
          {subheading}
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <a
            href="#"
            className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-slate-900 bg-white hover:bg-slate-100 rounded-brand shadow-lg transition-all hover:scale-105 active:scale-95"
          >
            Get Started Now
            <ArrowRight className="ml-2 h-5 w-5" />
          </a>
          <a
            href="#features"
            className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-brand transition-all"
          >
            Learn More
          </a>
        </div>

        <div className="pt-4 flex items-center justify-center gap-2 text-xs text-slate-400">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>No credit card required • Instant access • Fully open-source</span>
        </div>
      </div>
    </section>
  );
}}
"""

    def _build_footer_component(self, spec: WebsiteSpec) -> str:
        brand = spec.navigation.brandName or spec.title.split("-")[0].strip() or "Replicate.AI"
        return f"""import React from 'react';

export default function Footer() {{
  return (
    <footer className="bg-slate-950 text-slate-400 py-14 border-t border-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8">
          <div className="col-span-2 space-y-4">
            <div className="flex items-center gap-2 text-white font-bold text-lg">
              <div className="h-8 w-8 rounded-brand bg-primary flex items-center justify-center text-white text-sm font-extrabold">
                {brand[:2].upper()}
              </div>
              <span>{brand}</span>
            </div>
            <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
              Autonomously reconstructed by Replicate.AI. Clean, modular React components, responsive layouts, and modern typography.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3">Product</h4>
            <ul className="space-y-2 text-xs">
              <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
              <li><a href="#solutions" className="hover:text-white transition-colors">Solutions</a></li>
              <li><a href="#pricing" className="hover:text-white transition-colors">Pricing</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3">Company</h4>
            <ul className="space-y-2 text-xs">
              <li><a href="#" className="hover:text-white transition-colors">About</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200 mb-3">Legal</h4>
            <ul className="space-y-2 text-xs">
              <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 mt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-600 gap-4">
          <p>© {{new Date().getFullYear()}} {brand}. All rights reserved.</p>
          <p>Reconstructed frontend powered by Replicate.AI autonomous agent.</p>
        </div>
      </div>
    </footer>
  );
}}
"""

    def _build_app_tsx(self, spec: WebsiteSpec) -> str:
        return """import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import Testimonials from './components/Testimonials';
import CTA from './components/CTA';
import Footer from './components/Footer';

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-brandBg text-brandText selection:bg-primary selection:text-white font-sans">
      <Navbar />
      <main className="flex-grow">
        <Hero />
        <Features />
        <Testimonials />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
"""

    def _build_project_readme(self, spec: WebsiteSpec) -> str:
        return f"""# {spec.title}

> Reconstructed frontend generated by **Replicate.AI**.

## Original Source
- **URL**: {spec.url}
- **Framework**: Independent React 18 + TypeScript + Tailwind CSS + Vite
- **Components**: Reusable, modular components in `src/components/`

## Running Locally

```bash
# 1. Install dependencies
npm install

# 2. Run dev server
npm run dev

# 3. Build for production
npm run build

# 4. Preview production build
npm run preview
```
"""

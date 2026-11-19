Buatkan desain web aplikasi dengan tampilan profesional, modern, bersih, dan premium menggunakan **Tailwind CSS**.

Fokus utama:

1. Gaya visual
- Minimalis, elegan, dan rapi.
- Gunakan whitespace yang cukup agar nyaman dibaca.
- Border radius halus (`rounded-xl` sampai `rounded-2xl`), shadow lembut, dan transisi smooth.

2. Warna
- Gunakan palet warna profesional:
  - Primary: `#2563EB`
  - Secondary: `#0F172A`
  - Accent: `#14B8A6`
  - Background: `#F8FAFC`
  - Text utama: `#0B1220`
  - Text sekunder: `#475569`
- Pastikan kontras tinggi dan aksesibilitas baik (WCAG friendly).

3. Typography & gaya penulisan
- Gunakan font modern (Inter / Poppins / Plus Jakarta Sans).
- Headline tegas, deskripsi ringkas, CTA jelas.
- Tone copywriting: profesional, meyakinkan, tidak bertele-tele.
- Contoh gaya teks:
  - Judul: “Kelola data lebih cepat dan terstruktur”
  - Subjudul: “Platform modern untuk meningkatkan efisiensi kerja tim Anda.”

4. Komponen Card
- Gunakan card dengan class Tailwind seperti:
  - `bg-white/80 backdrop-blur-sm`
  - `rounded-2xl`
  - `shadow-sm hover:shadow-lg`
  - `border border-slate-200/60`
  - `transition duration-300`
- Hover effect: naik sedikit (`hover:-translate-y-1`) dengan transisi halus.
- Isi card terstruktur: ikon, judul, deskripsi singkat, tombol aksi.

5. Efek Glassmorphism
- Terapkan pada navbar/panel tertentu dengan Tailwind utility:
  - `bg-white/10` atau `bg-white/20`
  - `backdrop-blur-md` / `backdrop-blur-lg`
  - `border border-white/20`
- Gunakan secukupnya agar tetap elegan dan tidak mengganggu keterbacaan.

6. Opacity & layer
- Gunakan overlay gradient/opacity untuk hero section agar teks tetap terbaca:
  - contoh: `bg-gradient-to-b from-slate-900/60 to-slate-900/20`
- Hindari opacity berlebihan yang membuat elemen pudar.
- Prioritaskan hierarchy visual: elemen penting harus paling menonjol.

7. Layout & Responsiveness
- Gunakan grid/flex modern Tailwind.
- Mobile-first responsive (`sm`, `md`, `lg`, `xl` breakpoints).
- Navbar sticky, hero kuat, section fitur, statistik, testimoni, dan footer rapi.
- Gunakan container konsisten: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`.

8. Micro-interaction
- Animasi ringan (fade, slide-up, hover).
- Durasi transisi 200–300ms (`duration-200` atau `duration-300`).
- Hindari animasi berlebihan agar tetap profesional.

Output yang diinginkan:
- Struktur HTML semantic + class Tailwind yang siap pakai.
- Desain konsisten secara warna, tipografi, spacing, dan komponen.
- UI terasa profesional seperti produk SaaS modern dan siap production.
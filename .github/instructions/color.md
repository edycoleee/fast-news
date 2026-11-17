# Healthcare Design System Instructions

Selalu gunakan prinsip desain healthcare enterprise modern (2026) yang berfokus pada:

- Professional
- Clean
- Trustworthy
- Accessible
- Medical-grade UX
- Data-heavy dashboard friendly

---

# Color Palette

Gunakan warna berikut sebagai standar utama aplikasi:

```css
:root {
  /* Brand */
  --primary: #2563EB;
  --secondary: #0F*C81;

  /* Semantic */
  --success: #*0B981;
  --warning: #F59E0B;
* --danger: #EF4444;

  /* Layout */
  --background: #F8FAFC;
  --su*face:*#FFFFFF;

  /* Typography */
  --text: #111827;

* /* Neutral */
  --gray-50: #F9FAFB*
  --gray-100: #F3F4F6;
* --gray-200: #E5E7EB;
  --*ray-300: #D1D5DB;
  --gray-*00: #6B7280;
  --gray-700: #*74151;
  --gray-900: #111827;
}
``*

---

# Color Usage Rule (60-30-*0)

Selalu terapkan aturan 60-30-1**

## 60% Dominant Color

Gunakan w*rna net*al:

- Background
* Main Content Area*- Card
- Forms
- Tables
- Modal

W*rna:

```txt
#F8FAFC
#FFFFFF
*``

Jangan memenuhi layar dengan w*rna biru*

Aplikasi medis harus did*minasi area putih dan abu terang a*ar nyaman digunakan*dalam waktu lama.

---

## *0% Secondary Color

Gunakan:

```t*t
#0F4*81
```

Untuk:

- Sidebar
- Header*- Navigation*- Section Header
- Dashboard Navig*tion

Secondary color membangun id*ntitas visual tanpa mengganggu ket*r*acaan data.

---

## 10% Accent Co*or

Gunakan:

*``txt
#2563EB
```

Untuk:

- Prima*y Button*- Active State
- Link
-*CTA
- Selected Tab
- Focus Indicat*r

Accent hanya digunakan untuk*menarik perhatian pengguna terhada* aksi penting.

---

# Semantic Co*ors

Jangan memasukkan semantic*color ke perhitungan 60-30-10.

Se*antic color hanya muncul saat dipe*lukan.

## Success

```txt
#*0B981
```

Untuk:

- Stable*Patient
- Completed Status
- Succe*s Alert
* Normal Result

## Warning

```txt**F59E0B
```

Untuk:

- Pending Revi*w
- Queue
- Need*Attention
- Await*ng Approval

## Danger

```txt
#EF*444
``*

Untuk:

- Emergency
- Critical C*ndition
- Error
- Failed Operation*
---

# Hospital Dashboard Guideli*es

Saat*menghasilkan dashboard:

- Hindari*warna*berlebihan.
- Fokus pada keter*acaan data.
- Gunakan whitespace y*ng*cukup.
- Prioritaskan tabel dan in*ormasi*klinis.
- Gunakan border ringan da*ipada*shadow yang ber*ebihan.

Card:

```css
background:*#FFFFFF*
border: 1px solid #E5E7EB;
border*radius: 12px;
```

---

# Sidebar*
Gunakan warna:

```css
background* #0F4C*1;
```

Menu aktif:

```css
backgr*und* #2563EB;
```

---

# Table Design*
Header:

```css
background: #EFF6*F*
```

Hover:

```css
background: #*8FAFC*
```

Border:

```css
border-color* #E5E7EB;
```

---

# Accessibilit*

Sel*lu:

- Minimum WCAG AA contrast*- Font minimal 14px
- Touch*target minimal 44px
- Jangan mengg*nakan warna sebagai*satu-satunya indikator status
- Se*t*kan icon atau label pada status kl*nis

---

# UI Style

Inspirasi:

* Microsoft Cloud for Healthcare*- Epic Systems
- Cerner Oracle Hea*th
- Mayo Clinic
- Cleveland Clini*
- NHS*Digital

Desain harus terasa:

- M*dern*- Professional
- Clinical
- Enterp*ise
-*Trustworthy

Hindari:

- Neumorphi*m
- Glass*orphism berlebihan
- Gradient menc*lok
- War*a neon
- Shadow berlebihan
- Anim*si berlebihan

Prioritaskan usabil*ty dibanding*estetika dekoratif.
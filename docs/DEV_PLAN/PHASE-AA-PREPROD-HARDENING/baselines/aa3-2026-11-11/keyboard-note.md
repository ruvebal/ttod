# AA3 keyboard smoke note (2026-11-11)

Chrome on the isolated stack, keyboard only. Each step is also automated in `scripts/aa3-browser-check.mjs`.

1. On any page, the first Tab focuses "Saltar al contenido" / "Skip to content". Enter moves to `main#ttod-main`.
2. At ≥ 40rem: Tab goes through the brand, the four primary links, Biblioteca and Cuenta (or Entrar), then `EN`/`ES`.
   The current section has `aria-current="page"` and a 2 px underline.
3. Below 40rem: Tab reaches "Menú". Enter opens the panel below the bar (48 px rows), and Tab walks its rows and
   leaves it into the page; there is no trap. Escape closes it and returns focus to "Menú". An outside tap or
   click closes it without moving focus.
4. `/es/account/`: Tab moves through the name field and Save, the three password fields, each with its own
   "Mostrar …" toggle (`aria-pressed`), the "close my other sessions" checkbox, then Change, then the two sign-out
   buttons. A mismatch in "Repite" blocks submit before anything is sent.
5. Under `prefers-reduced-motion`, the bar never hides on scroll, and the login sky does not animate.

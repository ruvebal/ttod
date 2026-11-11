<script lang="ts">
	// El grafo del código de TTOD: lo que CodeGraphContext indexó sobre este repo,
	// servido como JSON estático (`/data/grafo-codigo.json`, hecho por
	// `scripts/exportar-grafo-codigo.mjs`). `/api/v1/graph` es el grafo de los
	// aforismos y no trae llamadas: las llamadas reales viven en este índice.
	//
	// Un símbolo cada vez, en el centro; quién lo llama llega por un lado y a quién
	// llama sale por el otro, agrupados por fichero. Entre los grupos y el centro,
	// un cauce de tinta por fichero cuyo grosor es el número de llamadas (forma de
	// sankey, trazada con d3-shape). Las cajas son HTML: botones de verdad,
	// plegables y legibles sin el dibujo, que solo es el cauce (aria-hidden).
	import { onMount, tick } from 'svelte';
	import { adyacencia, agrupa, cauces, rutaCorta, type Cauce, type Grupo, type Simbolo } from './codigoLayout';
	import { vigilarLaMano } from './calma';

	interface Props {
		lang: 'en' | 'es';
	}
	const { lang }: Props = $props();

	interface Datos {
		generado: string;
		repo: { nombre: string; commit: string; indexado: string | null };
		resumen: {
			ficheros: number;
			modulos_cuerpo: number;
			funciones: number;
			clases: number;
			interfaces: number;
			llamadas: number;
			herencias: number;
			descartados: number;
		};
		modulos: Array<{ id: string; simbolos: number; ficheros: number }>;
		simbolos: Simbolo[];
		llamadas: Array<[number, number] | [number, number, number]>;
	}

	const t = {
		en: {
			titulo: 'The code graph of this repository',
			intro: (d: Datos) =>
				`Indexed with CodeGraphContext at commit ${d.repo.commit}: ${d.resumen.funciones} functions, ${d.resumen.clases} classes and ${d.resumen.modulos_cuerpo} module bodies across ${d.resumen.ficheros} files, joined by ${d.resumen.llamadas} calls.`,
			buscar: 'Search a function or class',
			buscarAyuda: 'Type a name or a path',
			modulos: 'Folders',
			todos: 'All',
			indice: 'Index',
			resultados: (n: number, total: number) =>
				n < total ? `${n} of ${total} symbols` : `${n} symbols`,
			listaAyuda: 'Use the arrow keys to move, Enter to open a symbol.',
			verTodos: (n: number) => `Show all ${n}`,
			verFicheros: (n: number) => `Show ${n} more files`,
			sinResultados: 'No symbol matches that name.',
			entrada: 'Called by',
			salida: 'Calls',
			ficheros: (n: number) => (n === 1 ? '1 file' : `${n} files`),
			nadieLlama: 'Nobody calls it.',
			noLlama: 'It calls nothing indexed.',
			aislado: 'This symbol has no indexed calls in either direction.',
			linea: 'line',
			lineas: 'lines',
			args: (n: number) => (n === 1 ? '1 argument' : `${n} arguments`),
			complejidad: 'complexity',
			clase: { f: 'function', c: 'class', m: 'module body', i: 'interface' },
			heuristica: 'resolved by name (heuristic)',
			cuentas: (dentro: number, fuera: number) => `called by ${dentro} · calls ${fuera}`,
			clave: 'Each ribbon is one file; its width is how many calls it carries. Dotted: calls resolved by name only.',
			abrir: (n: string) => `Open ${n}`,
			cargando: 'Loading the code graph…',
			error: 'The code graph file is unavailable.',
			reintentar: 'Try again',
			vacio: 'The indexed graph has no symbols yet.',
			estado: (s: Simbolo, dentro: number, ficheros: number, fuera: number) =>
				`${s.n}: called by ${dentro} symbols in ${ficheros} files, calls ${fuera}.`,
			cuenta: 'What is counted',
			cuentaNota: (d: Datos) =>
				`Only Python, TypeScript and JavaScript symbols. The indexer also labelled ${d.resumen.descartados} CSS selectors as classes or functions; they are left out because they call nothing.`
		},
		es: {
			titulo: 'El grafo del código de este repositorio',
			intro: (d: Datos) =>
				`Indexado con CodeGraphContext en el commit ${d.repo.commit}: ${d.resumen.funciones} funciones, ${d.resumen.clases} clases y ${d.resumen.modulos_cuerpo} cuerpos de módulo repartidos en ${d.resumen.ficheros} ficheros, unidos por ${d.resumen.llamadas} llamadas.`,
			buscar: 'Busca una función o una clase',
			buscarAyuda: 'Escribe un nombre o una ruta',
			modulos: 'Carpetas',
			todos: 'Todas',
			indice: 'Índice',
			resultados: (n: number, total: number) =>
				n < total ? `${n} de ${total} símbolos` : `${n} símbolos`,
			listaAyuda: 'Muévete con las flechas y abre un símbolo con Intro.',
			verTodos: (n: number) => `Ver los ${n}`,
			verFicheros: (n: number) => `Ver ${n} ficheros más`,
			sinResultados: 'Ningún símbolo se llama así.',
			entrada: 'La llaman',
			salida: 'Llama a',
			ficheros: (n: number) => (n === 1 ? '1 fichero' : `${n} ficheros`),
			nadieLlama: 'No la llama nadie.',
			noLlama: 'No llama a nada indexado.',
			aislado: 'Este símbolo no tiene llamadas indexadas en ninguna dirección.',
			linea: 'línea',
			lineas: 'líneas',
			args: (n: number) => (n === 1 ? '1 argumento' : `${n} argumentos`),
			complejidad: 'complejidad',
			clase: { f: 'función', c: 'clase', m: 'cuerpo de módulo', i: 'interfaz' },
			heuristica: 'resuelta por nombre (heurística)',
			cuentas: (dentro: number, fuera: number) => `la llaman ${dentro} · llama a ${fuera}`,
			clave: 'Cada cauce es un fichero; su grosor, las llamadas que trae. Punteado: llamadas resueltas solo por el nombre.',
			abrir: (n: string) => `Abrir ${n}`,
			cargando: 'Cargando el grafo del código…',
			error: 'No se pudo cargar el fichero del grafo de código.',
			reintentar: 'Volver a intentarlo',
			vacio: 'El grafo indexado todavía no tiene símbolos.',
			estado: (s: Simbolo, dentro: number, ficheros: number, fuera: number) =>
				`${s.n}: la llaman ${dentro} símbolos de ${ficheros} ficheros y llama a ${fuera}.`,
			cuenta: 'Qué se cuenta',
			cuentaNota: (d: Datos) =>
				`Solo símbolos de Python, TypeScript y JavaScript. El indexador etiquetó además ${d.resumen.descartados} selectores CSS como clases o funciones; se dejan fuera porque no llaman a nada.`
		}
	}[lang];

	const TOPE = 60;
	/** Funciones que enseña cada grupo antes de su botón «Ver los n». */
	const TRAMO = 6;
	/** Ficheros por lado antes del botón «Ver n ficheros más». */
	const FICHEROS = 8;

	// El índice entero (869 símbolos, 1096 llamadas) va en crudo: con `$state`
	// normal Svelte envolvía cada objeto en un proxy y despertar la isla eran
	// 2201 ms de hilo (medido a 390 con la CPU a 1/4).
	let datos = $state.raw<Datos | null>(null);
	let error = $state('');
	let cargando = $state(true);
	let consulta = $state('');
	let modulo = $state('');
	let activo = $state<number | null>(null);
	let estrecho = $state(false);
	let listaEntera = $state(false);
	let focoLista = $state(0);

	// El dibujo: el hueco, si va en vertical, y los cauces medidos.
	let rioEl = $state<HTMLDivElement | null>(null);
	let centroEl = $state<HTMLElement | null>(null);
	let anchoRio = $state(0);
	let altoRio = $state(0);
	let trazos = $state<Cauce[]>([]);
	/** Grupo encendido (por puntero o por foco): `entrada-2`, `salida-0`… */
	let encendido = $state<string | null>(null);
	/** Grupos y funciones abiertos de más, por símbolo: se vacía al cambiar de símbolo. */
	let gruposAbiertos = $state<string[]>([]);
	let todosFicheros = $state<string[]>([]);

	/** El dibujo se apila cuando no le caben tres columnas, no por el tamaño del móvil. */
	const vertical = $derived(anchoRio > 0 ? anchoRio < 760 : estrecho);

	const vecinos = $derived.by(() => (datos ? adyacencia(datos.llamadas) : null));
	const entrantes = $derived((activo !== null && vecinos?.entrantes.get(activo)) || []);
	const salientes = $derived((activo !== null && vecinos?.salientes.get(activo)) || []);
	const gruposEntrada = $derived(datos ? agrupa(entrantes, datos.simbolos) : []);
	const gruposSalida = $derived(datos ? agrupa(salientes, datos.simbolos) : []);

	const grados = $derived.by(() => {
		if (!datos || !vecinos) return [];
		return datos.simbolos.map(
			(_, i) => (vecinos.entrantes.get(i)?.length ?? 0) + (vecinos.salientes.get(i)?.length ?? 0)
		);
	});

	const coincidencias = $derived.by(() => {
		if (!datos) return [] as number[];
		const q = consulta.trim().toLowerCase();
		const indices = datos.simbolos
			.map((_, i) => i)
			.filter((i) => {
				const s = datos!.simbolos[i];
				if (modulo && !s.f.startsWith(`${modulo}/`) && s.f !== modulo) return false;
				if (!q) return true;
				return s.n.toLowerCase().includes(q) || s.f.toLowerCase().includes(q);
			});
		return indices.sort((a, b) => (grados[b] ?? 0) - (grados[a] ?? 0));
	});

	const resultados = $derived(coincidencias.slice(0, TOPE));
	const listados = $derived(estrecho && !listaEntera ? resultados.slice(0, 12) : resultados);

	$effect(() => {
		if (focoLista >= listados.length) focoLista = 0;
	});

	// Al cambiar de símbolo el dibujo empieza de cero: nada encendido, nada abierto de más.
	$effect(() => {
		void activo;
		encendido = null;
		gruposAbiertos = [];
		todosFicheros = [];
	});

	function visibles(lado: 'entrada' | 'salida', grupos: Grupo[]) {
		return todosFicheros.includes(lado) ? grupos : grupos.slice(0, FICHEROS);
	}

	/** Mide dónde quedó cada boca y el centro, y traza los cauces. Barato: ~20 cajas. */
	function medir() {
		const rio = rioEl;
		const centro = centroEl;
		if (!rio || !centro) {
			trazos = [];
			return;
		}
		const r = rio.getBoundingClientRect();
		const c = centro.getBoundingClientRect();
		anchoRio = Math.round(r.width);
		altoRio = Math.round(r.height);
		const caja = { x: c.left - r.left, y: c.top - r.top, w: c.width, h: c.height };
		const bocas = (lado: string) =>
			[...rio.querySelectorAll<HTMLElement>(`[data-boca^="${lado}-"]`)].map((el) => {
				const b = el.getBoundingClientRect();
				return { x: b.left - r.left + b.width / 2, y: b.top - r.top + b.height / 2 };
			});
		const presupuesto = vertical ? 30 : Math.min(c.height * 0.7, 96);
		trazos = [
			...cauces('entrada', bocas('entrada'), gruposEntrada, caja, vertical, presupuesto),
			...cauces('salida', bocas('salida'), gruposSalida, caja, vertical, presupuesto)
		];
	}

	let pedido = 0;
	function remedir() {
		cancelAnimationFrame(pedido);
		pedido = requestAnimationFrame(() => medir());
	}

	// Se vuelve a medir cuando cambia lo que se dibuja; el tamaño lo vigila el observador.
	$effect(() => {
		void [activo, vertical, gruposAbiertos.length, todosFicheros.length, rioEl, centroEl];
		tick().then(remedir);
	});

	$effect(() => {
		const el = rioEl;
		if (!el || typeof ResizeObserver === 'undefined') return;
		const ojo = new ResizeObserver(() => remedir());
		ojo.observe(el);
		return () => ojo.disconnect();
	});

	/** Rótulo del filtro: una carpeta acaba en «/»; un fichero suelto (`cli.py`) no. */
	const carpeta = (id: string) => (/\.[a-z]+$/i.test(id) ? id : `${id}/`);

	function simbolo(i: number) {
		return datos?.simbolos[i];
	}

	function clave(s: Simbolo) {
		return `${s.f}:${s.l}`;
	}

	function activa(i: number, empuja = true) {
		activo = i;
		const s = simbolo(i);
		if (!s || typeof window === 'undefined') return;
		const url = new URL(window.location.href);
		url.searchParams.set('s', clave(s));
		history[empuja ? 'pushState' : 'replaceState'](null, '', url);
	}

	/** Elegir desde el dibujo: el símbolo pasa al centro y el foco va con él. */
	async function elige(i: number) {
		activa(i);
		await tick();
		const nombre = document.getElementById('codigo-centro-nombre');
		if (!nombre) return;
		nombre.focus({ preventScroll: true });
		const quieto = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		centroEl?.scrollIntoView({ block: 'center', behavior: quieto ? 'auto' : 'smooth' });
	}

	function abreGrupo(clave: string) {
		if (!gruposAbiertos.includes(clave)) gruposAbiertos = [...gruposAbiertos, clave];
	}

	/** Flechas, Inicio y Fin dentro de la lista del índice (una sola parada de tabulador). */
	function rueda(e: KeyboardEvent, total: number, foco: number, prefijo: string) {
		let n = foco;
		if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = Math.min(foco + 1, total - 1);
		else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') n = Math.max(foco - 1, 0);
		else if (e.key === 'Home') n = 0;
		else if (e.key === 'End') n = total - 1;
		else return null;
		e.preventDefault();
		document.getElementById(`${prefijo}-${n}`)?.focus();
		return n;
	}

	function esEntrar(e: KeyboardEvent) {
		return e.key === 'Enter' || e.key === ' ';
	}

	function desdeUrl() {
		if (!datos) return;
		const pedido = new URLSearchParams(window.location.search).get('s');
		const encontrado = pedido ? datos.simbolos.findIndex((s) => clave(s) === pedido) : -1;
		if (encontrado >= 0) {
			activo = encontrado;
			return;
		}
		// Puerta de entrada: el símbolo más conectado del repositorio, no uno al azar.
		let mejor = 0;
		for (let i = 1; i < grados.length; i += 1) if (grados[i] > grados[mejor]) mejor = i;
		activo = datos.simbolos.length ? mejor : null;
	}

	/**
	 * Pide el índice. Nunca se queda en «Cargando…»: si la página ya lo pidió
	 * (ver el `<script>` de `graph.astro`) se usa ese pedido; si no llega en 8 s
	 * se pide aquí con su propio plazo, y si tampoco, se dice y se ofrece repetir.
	 * No depende de WebGL ni de la isla del 3D de al lado.
	 */
	async function pide(): Promise<Datos> {
		const plazo = <T,>(p: Promise<T>, ms: number) =>
			Promise.race([p, new Promise<null>((listo) => setTimeout(() => listo(null), ms))]);
		const previo = (globalThis as Record<string, any>).__codigoDatos;
		(globalThis as Record<string, any>).__codigoDatos = null;
		const yaPedido = previo ? await plazo(previo as Promise<Datos | null>, 8000).catch(() => null) : null;
		if (yaPedido) return yaPedido;
		const r = await fetch('/data/grafo-codigo.json', { cache: 'no-store', signal: AbortSignal.timeout(10000) });
		const recibido = r.ok ? ((await r.json()) as Datos) : null;
		if (!recibido || !Array.isArray(recibido.simbolos)) throw new Error(t.error);
		return recibido;
	}

	let carga: () => void = () => {};

	onMount(() => {
		let vivo = true;
		const mano = vigilarLaMano();
		const consulta = window.matchMedia('(max-width: 60rem)');
		estrecho = consulta.matches;
		const alCambiar = (e: MediaQueryListEvent) => (estrecho = e.matches);
		consulta.addEventListener('change', alCambiar);
		const alVolver = () => desdeUrl();
		window.addEventListener('popstate', alVolver);
		// Las fuentes cambian el alto de las cajas: al llegar, los cauces se rehacen.
		document.fonts?.ready.then(() => vivo && remedir());

		carga = () => {
			cargando = true;
			error = '';
			pide()
				.then((recibido) =>
					// Dibujar esto por primera vez es una tarea de ~185 ms a 390 con la
					// CPU a 1/4: se espera a que la mano pare, con tope (ver calma.ts).
					mano.cuandoHayaCalma(300, () => {
						if (!vivo) return;
						datos = recibido;
						desdeUrl();
						cargando = false;
					})
				)
				.catch(() => {
					if (!vivo) return;
					error = t.error;
					cargando = false;
				});
		};
		carga();

		return () => {
			vivo = false;
			mano.parar();
			cancelAnimationFrame(pedido);
			consulta.removeEventListener('change', alCambiar);
			window.removeEventListener('popstate', alVolver);
		};
	});
</script>

{#snippet partido(nombre: string)}{#each nombre.split('_') as parte, j}{j ? '_' : ''}{#if j}<wbr />{/if}{parte}{/each}{/snippet}

{#snippet ladoDelRio(lado: 'entrada' | 'salida', grupos: Grupo[], total: number)}
	{@const titulo = lado === 'entrada' ? t.entrada : t.salida}
	{@const vistos = visibles(lado, grupos)}
	<section class={`rio__lado rio__lado--${lado}`} aria-labelledby={`rio-${lado}`}>
		<h3 class="rio__titulo" id={`rio-${lado}`}>
			{titulo} <span class="rio__num">({total})</span>
			{#if grupos.length}<span class="rio__sub">· {t.ficheros(grupos.length)}</span>{/if}
		</h3>
		{#if grupos.length === 0}
			<p class="rio__nada">{lado === 'entrada' ? t.nadieLlama : t.noLlama}</p>
		{:else}
			<ul class="rio__grupos">
				{#each vistos as g, k (`${activo}-${g.fichero}`)}
					{@const id = `${lado}-${k}`}
					{@const entero = gruposAbiertos.includes(id)}
					<li
						class="rio__grupo"
						class:encendido={encendido === id}
						onpointerenter={() => (encendido = id)}
						onpointerleave={() => (encendido = null)}
						onfocusin={() => (encendido = id)}
						onfocusout={() => (encendido = null)}
					>
						<details open={k < (vertical ? 1 : 3)} ontoggle={remedir}>
							<summary title={g.fichero}>
								<span class="rio__boca" data-boca={id} aria-hidden="true"></span>
								<span class="rio__fichero">{rutaCorta(g.fichero) || '—'}</span>
								<span class="rio__veces">· {g.lista.length}</span>
							</summary>
							<ul class="rio__funciones">
								{#each entero ? g.lista : g.lista.slice(0, TRAMO) as [i, heuristica] (i)}
									{@const v = datos!.simbolos[i]}
									<li>
										<button
											type="button"
											class="rio__funcion"
											data-clase={v.t}
											aria-label={`${t.abrir(v.n)} — ${t.clase[v.t]} — ${v.f}:${v.l}${heuristica ? ` — ${t.heuristica}` : ''}`}
											onclick={() => elige(i)}
										>
											<span class="rio__nombre">{@render partido(v.n)}</span>
											<span class="rio__linea">:{v.l}{heuristica ? ' ≈' : ''}</span>
										</button>
									</li>
								{/each}
							</ul>
							{#if !entero && g.lista.length > TRAMO}
								<button type="button" class="codigo__mas" onclick={() => abreGrupo(id)}>
									{t.verTodos(g.lista.length)}
								</button>
							{/if}
						</details>
					</li>
				{/each}
			</ul>
			{#if vistos.length < grupos.length}
				<button
					type="button"
					class="codigo__mas"
					onclick={() => (todosFicheros = [...todosFicheros, lado])}
				>
					{t.verFicheros(grupos.length - vistos.length)}
				</button>
			{/if}
		{/if}
	</section>
{/snippet}

<section class="codigo" aria-labelledby="codigo-titulo">
	<header class="codigo__cabecera">
		<h2 id="codigo-titulo">{t.titulo}</h2>
		{#if datos?.resumen}<p class="codigo__intro">{t.intro(datos)}</p>{/if}
	</header>

	{#if cargando}
		<p class="codigo__aviso" role="status">{t.cargando}</p>
	{:else if error}
		<div class="codigo__aviso" role="alert">
			<p>{error}</p>
			<button type="button" class="codigo__mas" onclick={() => carga()}>{t.reintentar}</button>
		</div>
	{:else if datos && datos.simbolos.length === 0}
		<p class="codigo__aviso">{t.vacio}</p>
	{:else if datos}
		<div class="codigo__cuerpo">
			<search class="codigo__filtros">
				<label class="codigo__campo" for="codigo-buscar">
					<span>{t.buscar}</span>
					<input
						id="codigo-buscar"
						type="search"
						bind:value={consulta}
						placeholder={t.buscarAyuda}
						autocomplete="off"
					/>
				</label>

				<div class="codigo__modulos-grupo">
					<p class="codigo__rotulo" id="codigo-modulos">{t.modulos}</p>
					<ul class="codigo__modulos" aria-labelledby="codigo-modulos">
						<li>
							<button type="button" aria-pressed={modulo === ''} onclick={() => (modulo = '')}>
								{t.todos}
							</button>
						</li>
						{#each (datos.modulos ?? []).slice(0, 8) as m}
							<li>
								<button
									type="button"
									aria-pressed={modulo === m.id}
									onclick={() => (modulo = modulo === m.id ? '' : m.id)}
								>
									<span>{carpeta(m.id)}</span><span class="codigo__cuenta">· {m.simbolos}</span>
								</button>
							</li>
						{/each}
					</ul>
				</div>
			</search>

			{#if activo !== null && datos.simbolos[activo]}
				{@const s = datos.simbolos[activo]}
				<p class="codigo__estado visually-hidden" aria-live="polite" aria-atomic="true">
					{t.estado(s, entrantes.length, gruposEntrada.length, salientes.length)}
				</p>
				<div
					class="rio"
					class:rio--vertical={vertical}
					class:rio--encendido={encendido !== null}
					bind:this={rioEl}
				>
					<svg class="rio__cauces" width={anchoRio} height={altoRio} aria-hidden="true">
						{#each trazos as c (`${activo}-${c.lado}-${c.k}`)}
							<path
								d={c.d}
								class={`rio__cauce rio__cauce--${c.lado}`}
								class:heuristica={c.heuristica}
								class:encendido={encendido === `${c.lado}-${c.k}`}
							/>
						{/each}
					</svg>

					{@render ladoDelRio('entrada', gruposEntrada, entrantes.length)}

					<article class="rio__centro" bind:this={centroEl} aria-labelledby="codigo-centro-nombre">
						<p class="rio__tipo" data-clase={s.t}>{t.clase[s.t]} · {s.g}</p>
						<h3 class="rio__protagonista" id="codigo-centro-nombre" tabindex="-1">{@render partido(s.n)}</h3>
						<p class="rio__ruta">{s.f} · {t.lineas} {s.l}–{s.L}</p>
						{#if s.a || s.c}
							<p class="rio__ruta">
								{#if s.a}{t.args(s.a)}{/if}{#if s.a && s.c} · {/if}{#if s.c}{t.complejidad} {s.c}{/if}
							</p>
						{/if}
						<p class="rio__cuentas">{t.cuentas(entrantes.length, salientes.length)}</p>
						{#if entrantes.length === 0 && salientes.length === 0}
							<p class="rio__nada">{t.aislado}</p>
						{/if}
					</article>

					{@render ladoDelRio('salida', gruposSalida, salientes.length)}
				</div>
				<p class="codigo__clave">
					<svg viewBox="0 0 48 14" width="48" height="14" aria-hidden="true">
						<path d="M2 6 C25 6 25 1 46 1 L46 13 C25 13 25 8 2 8 Z" class="rio__cauce" />
					</svg>
					<svg viewBox="0 0 48 14" width="48" height="14" aria-hidden="true">
						<path d="M2 6 C25 6 25 3 46 3 L46 11 C25 11 25 8 2 8 Z" class="rio__cauce heuristica" />
					</svg>
					<span>{t.clave}</span>
				</p>
			{/if}

			<section class="codigo__indice" aria-labelledby="codigo-indice-titulo">
				<p class="codigo__rotulo" id="codigo-indice-titulo">
					{t.indice} · {t.resultados(resultados.length, coincidencias.length)}
				</p>
				{#if resultados.length === 0}
					<p class="codigo__aviso codigo__aviso--suave">{t.sinResultados}</p>
				{:else}
					<p class="codigo__ayuda">{t.listaAyuda}</p>
					<ul class="codigo__lista" role="listbox" aria-labelledby="codigo-indice-titulo">
						{#each listados as i, k (i)}
							{@const s = datos.simbolos[i]}
							<li
								id={`codigo-op-${k}`}
								role="option"
								class="codigo__item"
								tabindex={focoLista === k ? 0 : -1}
								aria-selected={activo === i}
								onclick={() => elige(i)}
								onkeydown={(e) => {
									if (esEntrar(e)) {
										e.preventDefault();
										elige(i);
										return;
									}
									const n = rueda(e, listados.length, k, 'codigo-op');
									if (n !== null) focoLista = n;
								}}
							>
								<span class="codigo__nombre" data-clase={s.t}>{s.n}</span>
								<span class="codigo__ruta">{rutaCorta(s.f)}</span>
							</li>
						{/each}
					</ul>
					{#if listados.length < resultados.length}
						<button type="button" class="codigo__mas" onclick={() => (listaEntera = true)}>
							{t.verTodos(resultados.length)}
						</button>
					{/if}
				{/if}
			</section>
		</div>

		{#if datos?.resumen}<p class="codigo__nota"><strong>{t.cuenta}.</strong> {t.cuentaNota(datos)}</p>{/if}
	{/if}
</section>

<style>
	.codigo {
		--tinta-entrada: #5b4a2f;
		--tinta-salida: #8a2f22;
		/* El verde botánico del sistema da 4,36:1 sobre el papel a 14 px (axe lo
		   marca): aquí se usa un paso más oscuro, 5,25:1, para los nombres de clase. */
		--verde-clase: #3f6150;
		/* El borde de un control es su único contorno: 3,89:1 sobre el papel.
		   `--ttod-color-line` da 3,26:1 sobre la superficie elevada del buscador
		   pero solo 2,92:1 sobre el papel, donde viven los chips (WCAG 1.4.11). */
		--linea-control: #7a6c55;
		font-family: var(--ttod-font-ui);
		color: var(--ttod-color-ink);
	}
	.codigo__cabecera {
		max-width: 46rem;
		margin-bottom: var(--ttod-space-8);
	}
	h2 {
		font-family: var(--ttod-font-body);
		font-size: clamp(1.6rem, 3.4vw, 2.4rem);
		font-weight: 400;
		margin: 0 0 var(--ttod-space-3);
	}
	/* Esto se lee, no se consulta: a 14 px en móvil se quedaba corto (aviso de
	   revisar-pagina a 390). */
	.codigo__intro {
		margin: 0;
		font-size: var(--ttod-text-base);
		line-height: 1.7;
		color: var(--ttod-color-muted);
	}

	.codigo__filtros {
		display: flex;
		flex-wrap: wrap;
		align-items: end;
		gap: var(--ttod-space-4) var(--ttod-space-6);
	}
	/* Índice: buscador, módulos y resultados. La entrada es el nombre, como en
	   Sourcetrail; el árbol completo sería otra bola de 1000 ficheros. */
	.codigo__campo {
		flex: 1 1 18rem;
		max-width: 24rem;
	}
	.codigo__campo span {
		display: block;
		font-size: var(--ttod-text-ui);
		letter-spacing: var(--ttod-tracking-ui);
		text-transform: uppercase;
		color: var(--ttod-color-muted);
		margin-bottom: var(--ttod-space-3);
	}
	.codigo__campo input {
		width: 100%;
		padding: var(--ttod-space-3) var(--ttod-space-4);
		font: inherit;
		font-size: var(--ttod-text-sm);
		color: inherit;
		background: var(--ttod-color-surface-raised);
		border: 1px solid var(--linea-control);
		border-radius: var(--ttod-radius-sm);
	}
	/* El gris por defecto del navegador se queda en 3.2:1 sobre el papel. */
	.codigo__campo input::placeholder {
		color: var(--ttod-color-muted);
		opacity: 1;
	}
	.codigo__modulos-grupo {
		flex: 1 1 22rem;
	}
	.codigo__rotulo {
		margin: 0 0 var(--ttod-space-3);
		font-size: var(--ttod-text-ui);
		letter-spacing: var(--ttod-tracking-ui);
		text-transform: uppercase;
		color: var(--ttod-color-muted);
	}
	.codigo__ayuda {
		margin: 0 0 var(--ttod-space-3);
		font-size: 0.8rem;
		color: var(--ttod-color-muted);
	}
	.codigo__modulos,
	.codigo__lista {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.codigo__modulos {
		display: flex;
		flex-wrap: wrap;
		gap: var(--ttod-space-1);
	}
	/* En móvil el filtro se toca con el dedo: la píldora entera mide 44 px de
	   alto, no los 31 que medía (medido con revisar-pagina a 390 y 768). */
	.codigo__modulos button {
		font: inherit;
		font-size: 0.8rem;
		letter-spacing: 0.04em;
		display: inline-flex;
		align-items: center;
		/* El espacio que hay escrito entre el nombre del módulo y su cifra lo
		   borra el `inline-flex` (un hueco en blanco no llega a ser un hijo de
		   la caja), y en pantalla se leía «tests359». El hueco lo pone la caja. */
		gap: 0.45em;
		min-height: 44px;
		padding: 0 var(--ttod-space-4);
		color: var(--ttod-color-muted);
		background: none;
		border: 1px solid var(--linea-control);
		border-radius: 999px;
		cursor: pointer;
	}
	.codigo__modulos button:hover {
		color: var(--ttod-color-ink);
		border-color: var(--ttod-color-ink);
	}
	.codigo__modulos button[aria-pressed="true"] {
		color: var(--ttod-color-paper);
		background: var(--ttod-color-ink);
		border-color: var(--ttod-color-ink);
	}

	.codigo__indice {
		margin-top: var(--ttod-space-6);
		padding-top: var(--ttod-space-8);
		border-top: 1px solid var(--ttod-color-line-subtle);
	}
	.codigo__lista {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(14rem, 1fr));
		gap: 0 var(--ttod-space-6);
	}
	.codigo__item {
		display: block;
		border-top: 1px solid var(--ttod-color-line-subtle);
		cursor: pointer;
	}
	.codigo__item {
		padding: var(--ttod-space-3) var(--ttod-space-1);
	}
	.codigo__item[aria-selected='true'] .codigo__nombre {
		color: var(--ttod-color-accent);
		font-weight: 600;
	}
	.codigo__mas {
		margin-top: var(--ttod-space-4);
		font: inherit;
		font-size: 0.8rem;
		display: inline-flex;
		align-items: center;
		min-height: 44px;
		padding: 0 var(--ttod-space-4);
		color: var(--ttod-color-ink);
		background: none;
		border: 1px solid var(--linea-control);
		border-radius: 999px;
		cursor: pointer;
	}
	.codigo__nombre {
		display: block;
		font-size: var(--ttod-text-sm);
		overflow-wrap: anywhere;
	}
	.codigo__nombre[data-clase='c'] {
		color: var(--verde-clase);
	}
	.codigo__nombre[data-clase='m'] {
		font-style: italic;
		color: var(--ttod-color-muted);
	}
	.codigo__ruta {
		display: block;
		font-size: 0.8rem;
		color: var(--ttod-color-muted);
		overflow-wrap: anywhere;
	}
	.codigo__cuenta {
		font-variant-numeric: tabular-nums;
		color: var(--ttod-color-muted);
	}
	.codigo__aviso {
		font-size: var(--ttod-text-sm);
		color: var(--ttod-color-muted);
	}
	.codigo__aviso--suave {
		margin: var(--ttod-space-3) 0 0;
	}
	.codigo__nota {
		max-width: 46rem;
		margin: var(--ttod-space-8) 0 0;
		font-size: 0.8rem;
		line-height: 1.7;
		color: var(--ttod-color-muted);
	}

	.codigo__item:hover .codigo__nombre,
	.rio__funcion:hover .rio__nombre {
		color: var(--ttod-color-accent);
	}

	.codigo__cuerpo {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: var(--ttod-space-8);
	}
	.visually-hidden {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip: rect(0 0 0 0);
		white-space: nowrap;
	}
	/* La barra de arriba es fija: lo que recibe el foco o el salto se para debajo.
	   Lo hace una sola regla global (`html { scroll-padding-top }` en `Page.astro`,
	   LOCATORS §6); un `scroll-margin` aquí se sumaba a ella. */

	/* ── El río: quien llama | el símbolo | a quién llama ── */
	.rio {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(15rem, 21rem) minmax(0, 1fr);
		column-gap: clamp(4.5rem, 9vw, 8.5rem);
		align-items: center;
		padding-block: var(--ttod-space-6);
	}
	.rio__cauces {
		position: absolute;
		inset: 0;
		overflow: visible;
		pointer-events: none;
		z-index: 0;
	}
	.rio__cauce {
		fill: var(--tinta-entrada);
		color: var(--tinta-entrada);
		fill-opacity: 0.3;
		stroke: none;
		mix-blend-mode: multiply;
		transition: fill-opacity 0.25s ease;
		animation: mana 0.7s cubic-bezier(0.2, 0.7, 0.3, 1) both;
	}
	.rio__cauce--salida {
		fill: var(--tinta-salida);
		color: var(--tinta-salida);
	}
	/* Resueltas solo por el nombre: la orilla punteada, sin agua dentro. */
	.rio__cauce.heuristica {
		fill-opacity: 0.06;
		stroke: currentColor;
		stroke-width: 1.2;
		stroke-dasharray: 3 3;
	}
	.rio--encendido .rio__cauce {
		fill-opacity: 0.08;
	}
	.rio--encendido .rio__cauce.encendido {
		fill-opacity: 0.7;
	}
	@keyframes mana {
		from {
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.rio__cauce {
			animation: none;
			transition: none;
		}
	}

	.rio__lado,
	.rio__centro {
		position: relative;
		z-index: 1;
		min-width: 0;
	}
	.rio__titulo {
		margin: 0 0 var(--ttod-space-3);
		font-size: var(--ttod-text-ui);
		letter-spacing: var(--ttod-tracking-ui);
		text-transform: uppercase;
		font-weight: 600;
		color: var(--ttod-color-ink);
	}
	.rio__num {
		font-variant-numeric: tabular-nums;
	}
	.rio__sub {
		font-weight: 400;
		color: var(--ttod-color-muted);
	}
	.rio__nada {
		margin: 0;
		font-size: var(--ttod-text-sm);
		color: var(--ttod-color-muted);
	}
	.rio__grupos,
	.rio__funciones {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.rio__grupo summary {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.45em;
		min-height: 44px;
		padding-inline: var(--ttod-space-1);
		border-top: 1px solid var(--ttod-color-line-subtle);
		font-size: var(--ttod-text-sm);
		list-style: none;
		cursor: pointer;
	}
	.rio__grupo summary::-webkit-details-marker {
		display: none;
	}
	/* La flecha del plegable, dibujada: el triángulo del navegador cambia en cada uno. */
	.rio__grupo summary::before {
		content: '';
		flex: none;
		width: 0.42rem;
		height: 0.42rem;
		border-right: 1.5px solid currentColor;
		border-bottom: 1.5px solid currentColor;
		transform: rotate(-45deg);
		transition: transform 0.2s ease;
	}
	.rio__grupo details[open] > summary::before {
		transform: rotate(45deg);
	}
	.rio__fichero {
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-weight: 500;
	}
	.rio__veces {
		flex: none;
		font-variant-numeric: tabular-nums;
		color: var(--ttod-color-muted);
	}
	/* La boca: donde nace el cauce de ese fichero. */
	.rio__boca {
		position: absolute;
		top: 50%;
		width: 9px;
		height: 9px;
		margin-top: -4.5px;
		border-radius: 50%;
		background: var(--ttod-color-paper);
		border: 2px solid var(--tinta-entrada);
		color: var(--tinta-entrada);
	}
	.rio__lado--entrada .rio__boca {
		right: -14px;
	}
	.rio__lado--salida .rio__boca {
		left: -14px;
		border-color: var(--tinta-salida);
	}
	.rio__grupo.encendido summary,
	.rio__grupo summary:hover {
		color: var(--ttod-color-accent);
	}
	.rio__grupo.encendido .rio__boca {
		background: currentColor;
	}
	.rio__funcion {
		display: block;
		width: 100%;
		min-height: 44px;
		padding: 0.55rem var(--ttod-space-1) 0.55rem 1.35rem;
		font: inherit;
		font-size: var(--ttod-text-sm);
		text-align: start;
		color: var(--ttod-color-ink);
		background: none;
		border: 0;
		border-radius: var(--ttod-radius-sm);
		cursor: pointer;
	}
	.rio__nombre {
		overflow-wrap: anywhere;
	}
	.rio__funcion[data-clase='c'] .rio__nombre {
		color: var(--verde-clase);
	}
	.rio__linea {
		margin-inline-start: 0.3em;
		white-space: nowrap;
		font-size: 0.8rem;
		font-variant-numeric: tabular-nums;
		color: var(--ttod-color-muted);
	}
	.rio__funcion:focus-visible,
	.rio__grupo summary:focus-visible,
	.rio__protagonista:focus-visible {
		outline: 3px solid var(--ttod-color-focus);
		outline-offset: 2px;
	}
	/* En horizontal los que llaman se alinean hacia el centro, como en un sankey. */
	.rio:not(.rio--vertical) .rio__lado--entrada {
		text-align: end;
	}
	.rio:not(.rio--vertical) .rio__lado--entrada summary,
	.rio:not(.rio--vertical) .rio__lado--entrada .rio__funcion {
		justify-content: flex-end;
		text-align: end;
	}
	.rio:not(.rio--vertical) .rio__lado--entrada summary {
		padding-inline-end: var(--ttod-space-3);
	}
	.rio:not(.rio--vertical) .rio__lado--entrada .rio__funcion {
		padding: 0.55rem var(--ttod-space-3) 0.55rem var(--ttod-space-1);
	}

	/* El símbolo: papel sobre el río, con tinta. El nombre se marca con tamaño y
	   peso, nunca con un fondo de color (el blanco sobre crema no se leía). */
	.rio__centro {
		padding: var(--ttod-space-6);
		background:
			radial-gradient(120% 90% at 20% 0%, rgb(138 47 34 / 0.07), transparent 60%),
			var(--ttod-color-paper);
		border: 1.5px solid var(--ttod-color-accent);
		border-radius: 2rem 2rem 2rem 0.6rem;
		box-shadow: 0 18px 40px -26px rgb(27 23 16 / 0.55);
	}
	.rio__tipo {
		margin: 0 0 var(--ttod-space-2);
		font-size: var(--ttod-text-ui);
		letter-spacing: var(--ttod-tracking-ui);
		text-transform: uppercase;
		color: var(--ttod-color-muted);
	}
	.rio__protagonista {
		margin: 0;
		font-family: var(--ttod-font-titular);
		font-weight: 300;
		font-size: clamp(1.6rem, 3.2vw, 2.3rem);
		line-height: 1.1;
		color: var(--ttod-color-ink);
		overflow-wrap: anywhere;
		border-radius: 4px;
	}
	.rio__ruta {
		margin: var(--ttod-space-2) 0 0;
		font-size: 0.8rem;
		line-height: 1.5;
		color: var(--ttod-color-muted);
		overflow-wrap: anywhere;
	}
	.rio__cuentas {
		margin: var(--ttod-space-4) 0 0;
		padding-top: var(--ttod-space-3);
		border-top: 1px solid var(--ttod-color-line-subtle);
		font-size: var(--ttod-text-sm);
		font-variant-numeric: tabular-nums;
		color: var(--ttod-color-ink);
	}

	/* ── En vertical (móvil): arriba quien llama, el símbolo, abajo a quién llama.
	   El margen izquierdo es el río: cada fichero es un afluente que baja. ── */
	.rio--vertical {
		grid-template-columns: minmax(0, 1fr);
		row-gap: var(--ttod-space-12);
		padding-block: var(--ttod-space-2);
	}
	.rio--vertical .rio__lado {
		padding-inline-start: 2.75rem;
	}
	.rio--vertical .rio__lado--entrada .rio__boca,
	.rio--vertical .rio__lado--salida .rio__boca {
		left: calc(-2.75rem + 17px);
		right: auto;
	}
	.rio--vertical .rio__centro {
		padding: var(--ttod-space-4) var(--ttod-space-4) var(--ttod-space-4) 2.75rem;
		border-radius: 1.6rem 1.6rem 1.6rem 0.5rem;
	}

	.codigo__clave {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--ttod-space-2) var(--ttod-space-3);
		margin: 0;
		font-size: 0.8rem;
		line-height: 1.5;
		color: var(--ttod-color-muted);
	}
	.codigo__clave svg {
		flex: none;
		overflow: visible;
	}
	.codigo__clave .rio__cauce {
		animation: none;
	}
	.codigo__clave .rio__cauce.heuristica {
		color: var(--tinta-entrada);
	}
	.codigo__clave span {
		flex: 1 1 16rem;
	}
	/* En el móvil las carpetas son una tira que se desliza con el dedo: apiladas,
	   ocho píldoras de 44 px eran media pantalla antes de llegar al dibujo. */
	@media (max-width: 40rem) {
		.codigo__modulos-grupo {
			flex: 1 1 100%;
			min-width: 0;
		}
		.codigo__modulos {
			flex-wrap: nowrap;
			overflow-x: auto;
			scroll-snap-type: x proximity;
			scrollbar-width: none;
			margin-inline: calc(var(--ttod-space-6) * -1);
			padding-inline: var(--ttod-space-6);
			mask-image: linear-gradient(90deg, transparent, #000 1.5rem, #000 calc(100% - 2.5rem), transparent);
		}
		.codigo__modulos li {
			flex: none;
			scroll-snap-align: start;
		}
		.codigo__modulos button {
			white-space: nowrap;
		}
	}
	.codigo__aviso p {
		margin: 0 0 var(--ttod-space-3);
	}
</style>

<script lang="ts">
  // La constelación de aforismos, en 3D de verdad (WebGL, `3d-force-graph` 1.73,
  // MIT: la misma librería de la referencia, danmaps/aoc2025 día 11).
  //
  // Dos cosas tiene que hacer, y las hace: **tocar un nodo da su ficha** (texto
  // entero, id, sección, nivel, etiquetas y vecinos, con la cámara volando hasta
  // él) y **elegir dos enciende el sendero** entre ambos, con la luz corriendo
  // por los hilos del camino. Abajo, el sendero se lee como una sola lección.
  //
  // Todo el dato es del backend real: `/api/v1/graph` (nodos y relaciones) y
  // `/api/v1/wisdom/sample` (la ficha de cada cita). Sin maquetas ni JSON fijo.
  import { onMount, tick } from 'svelte';
  import {
    caminoMasCorto,
    construirGrafo,
    desdeCorpus,
    plano2dRecordado,
    resumen,
    tintaDeSeccion,
    type EntradaCorpus,
    type GrafoSendero,
    type NodoSendero,
    type RespuestaGrafo,
  } from './sendero';
  // Los mismos rótulos que Sabiduría: en /es la sección y el nivel se leen en
  // español («Arquitectura», «Intermedio»), no con el slug del dato.
  import { rotuloNivel, rotuloSeccion } from '../../content/bosque';
  import { aliasDeNodos, escribirSendero, leerSendero, validarSendero } from './senderoUrl';

  interface Props { lang: 'en' | 'es' }
  const { lang }: Props = $props();

  const copia = {
    es: {
      titulo: 'El sendero entre dos aforismos',
      cargando: 'Buscando los aforismos…',
      montando: 'Levantando la constelación…',
      plana: 'Toca un aforismo para leerlo · al parar de bajar, la constelación gira en 3D',
      error: 'No hemos podido traer el corpus. Vuelve a intentarlo.',
      vacio: 'El corpus no trae ninguna relación entre aforismos todavía.',
      origen: 'Desde',
      destino: 'Hasta',
      busca: 'Busca un aforismo',
      buscaPista: 'tinta, contrato, prueba…',
      eligiendoDesde: 'Lo que elijas será el «desde»',
      eligiendoHasta: 'Lo que elijas será el «hasta»',
      coincidencias: (n: number, m: number) =>
        n === 1 ? '1 aforismo lo dice' : m < n ? `${n} aforismos lo dicen · los ${m} más conectados` : `${n} aforismos lo dicen`,
      sinCoincidencias: 'Ningún aforismo dice esa palabra.',
      ponerComo: (papel: string, texto: string) => `Poner como «${papel}»: ${texto}`,
      sinElegir: 'sin elegir',
      quitar: 'Quitar',
      azar: 'Dos al azar',
      limpiar: 'Limpiar',
      girar: 'Girar',
      pasos: (n: number) => (n === 1 ? '1 paso' : `${n} pasos`),
      sendero: 'El sendero',
      senderoCorto: 'Sendero',
      sinSendero: 'Sin sendero',
      nodos: 'Nodos',
      relaciones: 'Relaciones',
      sinCamino: 'No hay sendero entre estos dos: el corpus no los relaciona ni de lejos. Prueba con otro final.',
      pideDos: 'Toca un aforismo para abrir su ficha; marca uno como «desde» y otro como «hasta» y el camino entre ellos se enciende y se lee como una sola lección.',
      soloUno: 'Falta el segundo: toca otro aforismo y márcalo como «hasta».',
      leyenda: 'Leyenda',
      leyendaDesde: 'Desde',
      leyendaHasta: 'Hasta',
      leyendaPaso: 'Paso del sendero',
      leyendaResto: 'Aforismo por sección',
      leyendaHilo: 'Relación encendida',
      pista: 'Toca un nodo · arrastra para girar · pellizca o Ctrl + rueda para acercar',
      sinTraducir: 'sin traducir al español',
      verFicha: 'Ver la ficha entera',
      ficha: 'Ficha del aforismo',
      cerrar: 'Cerrar la ficha',
      volumen: 'Volumen',
      sinNivel: 'nivel sin dato',
      vecinos: 'Relacionados',
      desdeAqui: 'Desde aquí',
      hastaAqui: 'Hasta aquí',
      esDesde: 'Es el «desde»',
      esHasta: 'Es el «hasta»',
      conectados: 'Empieza por los más conectados',
      verPasos: 'Ver todos los pasos',
      sinWebgl: 'Constelación quieta: tu navegador no dibuja 3D · toca un aforismo para leerlo',
      nota: (n: number, a: number, c: number, t: number, e: number) =>
        `Se dibujan los ${n} aforismos que tienen alguna relación y sus ${a} relaciones. El corpus entero trae ${c} citas —${t} son la traducción al otro idioma— y ${e} aristas.`,
    },
    en: {
      titulo: 'The path between two aphorisms',
      cargando: 'Fetching the aphorisms…',
      montando: 'Raising the constellation…',
      plana: 'Tap an aphorism to read it · when you stop scrolling, the constellation turns in 3D',
      error: 'We could not load the corpus. Please try again.',
      vacio: 'The corpus carries no relations between aphorisms yet.',
      origen: 'From',
      destino: 'To',
      busca: 'Search an aphorism',
      buscaPista: 'ink, contract, test…',
      eligiendoDesde: 'What you pick becomes the “from”',
      eligiendoHasta: 'What you pick becomes the “to”',
      coincidencias: (n: number, m: number) =>
        n === 1 ? '1 aphorism says it' : m < n ? `${n} aphorisms say it · the ${m} most connected` : `${n} aphorisms say it`,
      sinCoincidencias: 'No aphorism says that word.',
      ponerComo: (papel: string, texto: string) => `Set as “${papel}”: ${texto}`,
      sinElegir: 'not picked',
      quitar: 'Remove',
      azar: 'Two at random',
      limpiar: 'Clear',
      girar: 'Spin',
      pasos: (n: number) => (n === 1 ? '1 step' : `${n} steps`),
      sendero: 'The path',
      senderoCorto: 'Path',
      sinSendero: 'No path yet',
      nodos: 'Nodes',
      relaciones: 'Links',
      sinCamino: 'There is no path between these two: the corpus never relates them. Try another end.',
      pideDos: 'Tap an aphorism to open its entry; mark one as “from” and another as “to” and the path between them lights up and reads as a single lesson.',
      soloUno: 'One more to go: tap another aphorism and mark it as “to”.',
      leyenda: 'Legend',
      leyendaDesde: 'From',
      leyendaHasta: 'To',
      leyendaPaso: 'Step on the path',
      leyendaResto: 'Aphorism by section',
      leyendaHilo: 'Lit relation',
      pista: 'Tap a node · drag to turn · pinch or Ctrl + wheel to zoom',
      sinTraducir: 'not translated',
      verFicha: 'Open the full entry',
      ficha: 'Aphorism entry',
      cerrar: 'Close the entry',
      volumen: 'Volume',
      sinNivel: 'level not given',
      vecinos: 'Related',
      desdeAqui: 'From here',
      hastaAqui: 'To here',
      esDesde: 'This is the “from”',
      esHasta: 'This is the “to”',
      conectados: 'Start with the most connected',
      verPasos: 'Show all steps',
      sinWebgl: 'Still constellation: your browser does not draw 3D · tap an aphorism to read it',
      nota: (n: number, a: number, c: number, t: number, e: number) =>
        `It draws the ${n} aphorisms that carry some relation and their ${a} relations. The whole corpus holds ${c} quotes —${t} of them the translation into the other language— and ${e} edges.`,
    },
  }[lang];

  let grafo = $state<GrafoSendero>({
    nodos: [],
    aristas: [],
    vecinos: new Map(),
    totales: { citas: 0, aristas: 0, traducciones: 0 },
  });
  let fichas = $state(new Map<string, EntradaCorpus>());
  let cargando = $state(true);
  let fallo = $state(false);
  let sinWebgl = $state(false);
  let origen = $state('');
  let destino = $state('');
  let abierta = $state('');
  /** El contenido de la hoja se está cruzando con el del nodo nuevo. */
  let cruzando = $state(false);
  let cruce = 0;
  let girando = $state(true);
  let filtro = $state('');
  /** Qué extremo del sendero se está eligiendo ahora mismo en el buscador. */
  let eligiendo = $state<'origen' | 'destino'>('origen');
  /** La isla sigue en pantalla (se apaga al desmontarla). */
  let vivoEnPantalla = true;
  let caja = $state<HTMLElement>();
  let escena = $state<HTMLElement>();
  let dormido = $state(false);
  let lienzo = $state<HTMLElement>();
  let panel = $state<HTMLElement>();
  let tituloEl = $state<HTMLElement>();
  /** El control que abrió la carta: ahí vuelve el foco al cerrarla. */
  let volverA: HTMLElement | null = null;
  /** Cuánto se ha bajado la carta con el dedo (móvil). */
  let arrastre = 0;

  const porId = $derived(new Map(grafo.nodos.map((n) => [n.id, n])));
  const camino = $derived(origen && destino ? caminoMasCorto(grafo.vecinos, origen, destino) : []);
  const enCamino = $derived(new Set(camino));
  const nodoAbierto = $derived(abierta ? porId.get(abierta) : undefined);
  const fichaAbierta = $derived(
    nodoAbierto ? fichas.get(nodoAbierto.idTexto) ?? fichas.get(nodoAbierto.id) : undefined,
  );
  const vecinosAbiertos = $derived(
    nodoAbierto
      ? (grafo.vecinos.get(nodoAbierto.id) ?? []).map((id) => porId.get(id)).filter((n) => n !== undefined)
      : [],
  );
  // Elegir los dos extremos era dos desplegables con 202 aforismos cada uno: 404
  // `<option>` que había que construir a plazos de diez para que no tiraran un
  // fotograma encima de quien baja la página (298 ms de hilo en el hueco + 231
  // de colocarlos, medido a 390 con la CPU a 1/4), y que en el móvil abren la
  // rueda del sistema con doscientas citas recortadas a 54 letras. Ahora se
  // busca: se escribe una palabra y salen como mucho seis aforismos, los más
  // conectados primero. Seis filas en vez de cuatrocientas opciones.
  const MAX_RESULTADOS = 6;
  const aguja = $derived(filtro.trim().toLocaleLowerCase(lang));
  /** Todos los que dicen la palabra (para decir cuántos hay, no para pintarlos). */
  const coincidencias = $derived(
    aguja ? grafo.nodos.filter((n) => n.texto.toLocaleLowerCase(lang).includes(aguja)) : grafo.nodos,
  );
  /**
   * Lo que se pinta: `grafo.nodos` ya viene ordenado por número de relaciones,
   * así que sin palabra esto es «los más conectados» —el mejor sitio por donde
   * empezar— y con palabra, los que más sendero pueden dar.
   */
  const resultados = $derived(coincidencias.slice(0, MAX_RESULTADOS));

  // La escena vive fuera del estado reactivo: cambia sesenta veces por segundo y
  // Svelte no tiene que enterarse de eso.
  let fg: any = null;
  /** El tamaño con el que está hecho el búfer de dibujo, para no rehacerlo por nada. */
  let anchoEscena = 0;
  let altoEscena = 0;
  let quitarToques: (() => void) | null = null;
  let nodosFg: any[] = [];
  let porIdFg = new Map<string, any>();
  let sinMovimiento = false;
  let siesta = 0;
  /** La escena está en marcha (el bucle de pintado corre). */
  let pintando = false;
  /** La constelación se está asentando (física a plazos, todavía sin pintar). */
  let montando = $state(false);
  /**
   * La constelación en 3D está en pie, asentada y pintada. Hasta entonces lo que
   * se ve es la misma constelación dibujada plana —las 202 estrellas y sus 332
   * hilos en un lienzo 2D, el mismo respaldo que usa un navegador sin WebGL— y
   * se toca igual. Antes aquí había un rótulo, «Levantando la constelación…», encima de
   * un cielo negro: la vista no existía hasta que había 3D, y en una máquina
   * lenta o con el backend a un segundo por llamada eso eran cinco segundos de
   * nada. Ahora la vista está entera desde el primer dato y el 3D es lo que
   * llega después, cuando la mano del visitante deja un hueco.
   */
  let tresDeVerdad = $state(false);
  /** Pantalla de dedo o estrecha: la escena se dibuja más barata (medido abajo). */
  let enMovil = false;
  /** La escena está a la vista (lo dice el `IntersectionObserver`). */
  let aLaVista = true;
  /** La página se está moviendo: mientras tanto no se pinta la escena. */
  let rodando = false;
  let finDeScroll = 0;
  /**
   * Cuánta quietud hace falta para volver a pintar el lienzo. En una máquina sin
   * tarjeta gráfica el primer fotograma de la constelación cuesta de 150 a 230 ms
   * (390, CPU a 1/4), así que volver a encenderla en la primera pausa del gesto
   * —180 ms bastaban— metía uno de esos fotogramas dentro del propio scroll:
   * cuatro empujones seguidos, cuatro tirones. Medio segundo de página quieta es
   * una pausa de verdad, no el hueco entre dos empujones del mismo dedo.
   */
  const ESPERA_PARA_PINTAR = 500;
  /** Lo que espera a que la página se quede quieta (ver `cuandoPareLaPagina`). */
  let enEspera: (() => void) | null = null;
  /** La máquina no da para pintar sesenta veces por segundo (se mide, abajo). */
  let flojo = $state(false);
  /**
   * El dedo que está encima de la constelación pero va hacia arriba o hacia
   * abajo: ese gesto es de la página. Mientras dure, la escena no gira ni se
   * pinta (ver `escucharToques`).
   */
  let gestoDeLaPagina = false;
  /**
   * El dedo que va de lado sobre la constelación: ese sí es del grafo, y
   * mientras gire se pinta aunque lleguen avisos de `touchmove`.
   */
  let gestoDelGrafo = false;
  /** Cuándo se movió por última vez algo por mano del visitante. */
  let ultimoMovimiento = 0;

  /**
   * Elegir desde el buscador: lo que toques ocupa el extremo que esté activo y
   * el buscador pasa al otro, así que dos toques seguidos trazan un sendero sin
   * tener que decir cada vez cuál es cuál. La cámara vuela allí para que se vea
   * dónde cae esa cita en la constelación (la ficha no se abre: tapa media
   * pantalla a 390 y aquí se está eligiendo, no leyendo).
   */
  function ponerExtremo(id: string) {
    if (!id) return;
    if (eligiendo === 'origen') {
      if (destino === id) destino = '';
      origen = id;
      eligiendo = 'destino';
    } else {
      if (origen === id) origen = '';
      destino = id;
      eligiendo = 'origen';
    }
    // Sin `verLaEscena()`: subir la página a la constelación dejaría el buscador
    // fuera de pantalla justo cuando falta elegir el otro extremo. La respuesta
    // se ve aquí mismo (el hueco se llena y la línea dice los pasos).
    volarA(id);
  }

  /** Quitar un extremo deja el buscador eligiendo ese hueco. */
  function quitarExtremo(papel: 'origen' | 'destino') {
    if (papel === 'origen') origen = '';
    else destino = '';
    eligiendo = papel;
  }

  function dosAlAzar() {
    // Dos extremos que de verdad tengan sendero: enseñar «no hay camino» de
    // entrada no explica la idea. Entre tres y seis pasos, que un sendero de
    // diez citas deja de leerse como una lección y pasa a ser una lista.
    const candidatos = grafo.nodos.filter((n) => n.grado > 0);
    if (candidatos.length < 2) return;
    for (let intento = 0; intento < 60; intento += 1) {
      const uno = candidatos[Math.floor(Math.random() * candidatos.length)];
      const otro = candidatos[Math.floor(Math.random() * candidatos.length)];
      if (uno.id === otro.id) continue;
      const prueba = caminoMasCorto(grafo.vecinos, uno.id, otro.id);
      if (prueba.length >= 4 && prueba.length <= 7) { origen = uno.id; destino = otro.id; return; }
    }
  }

  /**
   * `?from=&to=&node=` (AA3b): al llegar el grafo, la dirección manda; después,
   * lo que se elija se escribe en ella con `replaceState` (ver `senderoUrl.ts`).
   */
  let direccionLista = $state(false);
  function restaurarDeLaDireccion() {
    const pedido = validarSendero(leerSendero(window.location.search), aliasDeNodos(grafo.nodos));
    if (pedido.from) origen = pedido.from;
    if (pedido.to) destino = pedido.to;
    if (pedido.from && !pedido.to) eligiendo = 'destino';
    if (pedido.node) abierta = pedido.node;
    direccionLista = true;
  }
  $effect(() => {
    if (!direccionLista) return;
    const siguiente = escribirSendero(window.location.href, { from: origen, to: destino, node: abierta });
    const actual = `${window.location.pathname}${window.location.search}${window.location.hash}`;
    if (siguiente !== actual) history.replaceState(history.state, '', siguiente);
  });

  function limpiar() {
    clearTimeout(cruce);
    cruzando = false;
    origen = '';
    destino = '';
    abierta = '';
    eligiendo = 'origen';
  }

  /**
   * Abrir otro nodo con la hoja ya abierta no cierra la hoja: la hoja es un
   * marco estable y lo que cambia es lo que hay dentro. El contenido se cruza
   * (120 ms de salida + 120 de entrada) mientras la cámara vuela al nodo nuevo.
   */
  function abrir(id: string) {
    // De dónde venía el foco, para devolverlo al cerrar. Con la carta ya
    // abierta (un relacionado) se conserva el primero: cerrar vuelve al
    // control que la abrió, no a otro botón de la propia carta.
    if (!abierta) {
      const activo = document.activeElement;
      volverA = activo instanceof HTMLElement && activo !== document.body ? activo : null;
      arrastre = 0;
    }
    volarA(id);
    verLaEscena();
    if (!abierta || abierta === id || sinMovimiento) { abierta = id; return; }
    cruzando = true;
    clearTimeout(cruce);
    cruce = window.setTimeout(() => { abierta = id; cruzando = false; }, 120);
  }

  /**
   * Tocar un nodo con un dedo, no con un alfiler.
   *
   * La librería abre la ficha solo si el rayo da dentro de la esfera, y a 390 px
   * una esfera mide entre 2 y 7 px de radio (medido en vivo: de 81 puntos
   * alrededor del centro de un nodo, solo acertaban 3). Con el dedo —44 px— eso
   * es fallar la mitad de las veces sobre un nodo que se está viendo.
   *
   * Así que el toque lo resolvemos nosotros: de todos los aforismos que caen a
   * menos de un dedo del punto tocado, gana el que mejor puntúa en distancia
   * medida en «radios suyos», de modo que una esfera grande y cercana le gana a
   * una lejana y diminuta que casualmente cae más cerca del dedo. Es lo que hace
   * la persona: apunta a la bola que ve.
   */
  const RADIO_DEDO = 22;

  /** Lo que mide en pantalla el radio de la esfera de un nodo. */
  function radioEnPantalla(nodo: any, centro: { x: number; y: number }): number {
    const radio = 3.4 * Math.cbrt(Math.max(1, tamanoDeNodo(nodo)));
    const borde = fg.graph2ScreenCoords(nodo.x + radio, nodo.y, nodo.z);
    return Math.hypot(borde.x - centro.x, borde.y - centro.y);
  }

  /** El aforismo tocado, o `null` si el dedo cayó en el cielo. */
  function nodoTocado(x: number, y: number): string | null {
    if (!fg) return null;
    const camara = fg.camera();
    const mira = fg.controls()?.target ?? { x: 0, y: 0, z: 0 };
    // Hacia dónde mira la cámara: lo que queda detrás de ella se descarta, que
    // si no la proyección lo devuelve dado la vuelta, en mitad de la pantalla.
    const frente = { x: mira.x - camara.position.x, y: mira.y - camara.position.y, z: mira.z - camara.position.z };
    let elegido: string | null = null;
    let mejor = Infinity;
    for (const nodo of nodosFg) {
      const haciaElNodo =
        (nodo.x - camara.position.x) * frente.x +
        (nodo.y - camara.position.y) * frente.y +
        (nodo.z - camara.position.z) * frente.z;
      if (haciaElNodo <= 0) continue;
      const p = fg.graph2ScreenCoords(nodo.x, nodo.y, nodo.z);
      const distancia = Math.hypot(p.x - x, p.y - y);
      if (distancia > RADIO_DEDO) continue;
      const nota = distancia / (radioEnPantalla(nodo, p) + 6);
      if (nota < mejor) { mejor = nota; elegido = nodo.id; }
    }
    return elegido;
  }

  /**
   * Un toque es soltar donde se tocó: si el dedo se ha ido más de 12 px es que
   * estaba girando la escena, y girar no abre fichas.
   */
  function escucharToques(): () => void {
    let salida = { x: 0, y: 0, t: 0 };
    let repartido = false;
    const empieza = (e: PointerEvent) => {
      salida = { x: e.clientX, y: e.clientY, t: Date.now() };
      repartido = false;
      // Un dedo que acaba de apoyarse todavía no ha dicho qué quiere. Hasta que
      // lo diga —ocho píxeles más allá— no se pinta: pintar esos cuatro
      // fotogramas «por si acaso» eran los cuatro últimos tirones del arrastre
      // vertical (medido a 390 con la CPU a 1/4). Con el ratón no hace falta:
      // ahí el gesto vertical es la rueda, no el arrastre.
      if (e.pointerType === 'touch') {
        gestoDeLaPagina = true;
        dormir();
      }
    };
    /**
     * De quién es este gesto. La pista lo promete y el CSS lo escribe
     * (`touch-action: pan-y`): el dedo que sube o baja es de la página, el que
     * va de lado gira la constelación. Pero `touch-action` solo le habla al
     * navegador; el control de órbita de three escucha el dedo igual, por
     * `document` y con el puntero capturado, así que con un gesto vertical la
     * página bajaba **y** la constelación giraba a la vez. Girar cuesta aquí
     * cincuenta milisegundos de fotograma (medido a 390 con la CPU a 1/4: 26
     * fotogramas por encima de 50 ms en seis segundos de arrastre vertical, y
     * ninguno cuando la escena no gira), y nadie ha pedido ese giro: lo que
     * quería era leer lo de abajo. En cuanto el gesto se declara vertical, la
     * escena lo suelta —no gira y no se pinta— y el dedo es entero de la
     * página. El de lado sigue girando como siempre.
     */
    const mueve = (e: PointerEvent) => {
      if (repartido || !fg) return;
      const dx = Math.abs(e.clientX - salida.x);
      const dy = Math.abs(e.clientY - salida.y);
      if (Math.max(dx, dy) < 8) return;
      repartido = true;
      const mandos: any = fg.controls();
      if (dy > dx * 1.3) {
        // Vertical: de la página. La escena lo suelta y se queda quieta.
        gestoDeLaPagina = true;
        if (mandos) mandos.enabled = false;
        dormir();
        return;
      }
      // De lado: de la constelación. Se pinta mientras el dedo la gire.
      gestoDeLaPagina = false;
      gestoDelGrafo = true;
      rodando = false;
      if (mandos) mandos.enabled = true;
      despertar();
    };
    /**
     * El control vuelve en cuanto el dedo se va: `onPointerUp` de three no mira
     * `enabled`, así que suelta el puntero y se queda en reposo igual.
     */
    const soltar = () => {
      gestoDelGrafo = false;
      if (!gestoDeLaPagina) return;
      gestoDeLaPagina = false;
      const mandos: any = fg?.controls();
      if (mandos) mandos.enabled = true;
    };
    const acaba = (e: PointerEvent) => {
      soltar();
      if (!fg || !lienzo) return;
      if (Math.hypot(e.clientX - salida.x, e.clientY - salida.y) > 12) return;
      if (Date.now() - salida.t > 700) return;
      const caja = lienzo.getBoundingClientRect();
      const id = nodoTocado(e.clientX - caja.left, e.clientY - caja.top);
      if (id) abrir(id);
      else limpiarFicha();
    };
    lienzo.addEventListener('pointerdown', empieza, { passive: true });
    lienzo.addEventListener('pointermove', mueve, { passive: true });
    lienzo.addEventListener('pointerup', acaba, { passive: true });
    // Un gesto cancelado NO es un toque: cuando el navegador se queda el dedo
    // para bajar la página manda `pointercancel`, y a veces antes de los doce
    // píxeles del toque. Tratarlo como toque abría una ficha a quien solo
    // quería bajar. Aquí solo se devuelve el control.
    lienzo.addEventListener('pointercancel', soltar, { passive: true });
    return () => {
      lienzo?.removeEventListener('pointerdown', empieza);
      lienzo?.removeEventListener('pointermove', mueve);
      lienzo?.removeEventListener('pointerup', acaba);
      lienzo?.removeEventListener('pointercancel', soltar);
    };
  }

  /** La ficha es una región de la escena: si la escena no se ve, se trae. */
  function verLaEscena() {
    if (!escena) return;
    const sitio = escena.getBoundingClientRect();
    const visible = Math.min(sitio.bottom, window.innerHeight) - Math.max(sitio.top, 0);
    if (visible > sitio.height * 0.6) return;
    escena.scrollIntoView({ behavior: sinMovimiento ? 'auto' : 'smooth', block: 'start' });
  }

  /**
   * El grafo del backend. Se pide a la vez que el corpus, no detrás: en serie,
   * la segunda llamada no empezaba hasta el segundo 2,9 y la constelación no
   * aparecía hasta el 4,8 (medido a 390 con 4G lenta). A la vez, los dos
   * conjuntos de datos están en el segundo 3. Si el endpoint no contesta, el
   * grafo se arma con el corpus (lo decide quien llama, que ya lo tiene).
   */
  async function traerGrafo(): Promise<RespuestaGrafo | null> {
    try {
      const datos: RespuestaGrafo = await (pedido()?.grafo ?? comoJson('/api/v1/graph'));
      return datos?.nodes?.length ? datos : null;
    } catch {
      return null;
    }
  }

  /**
   * Lo que la página ya pidió al leerse (ver el `<script>` de `graph.astro`). Si
   * ese trozo no llegó a correr, la isla lo pide por su cuenta.
   */
  const pedido = (): { corpus: Promise<any>; grafo: Promise<any> } | null =>
    (globalThis as any).__senderoDatos ?? null;
  const comoJson = (ruta: string) =>
    fetch(ruta, { headers: { accept: 'application/json' } }).then((r) => (r.ok ? r.json() : null));

  /** El corpus entero: de aquí salen nivel, etiquetas y qué enseña cada cita. */
  async function traerCorpus(): Promise<EntradaCorpus[] | null> {
    try {
      const entradas: EntradaCorpus[] = await (pedido()?.corpus ?? comoJson('/api/v1/wisdom/sample'));
      return Array.isArray(entradas) ? entradas : null;
    } catch {
      return null;
    }
  }

  // ——— La escena ———————————————————————————————————————————————

  /** Clave de un hilo, siempre ordenada, para saber si está en el sendero. */
  function clave(a: string, b: string) { return a < b ? `${a}|${b}` : `${b}|${a}`; }
  const hilosDelCamino = $derived.by(() => {
    const juego = new Set<string>();
    for (let i = 0; i < camino.length - 1; i += 1) juego.add(clave(camino[i], camino[i + 1]));
    return juego;
  });

  function idDe(extremo: any): string { return typeof extremo === 'object' ? extremo.id : extremo; }

  function colorDeNodo(nodo: any): string {
    if (nodo.id === origen) return '#6fd39b';
    if (nodo.id === destino) return '#ff7a5c';
    if (enCamino.has(nodo.id)) return '#f6ecd4';
    if (nodo.id === abierta) return '#fff6e0';
    const tinta = tintaDeSeccion(nodo.seccion);
    // Con un sendero encendido, el resto de la constelación se retira: sigue
    // estando —es el mapa— pero deja de competir con el camino.
    return camino.length > 1 ? `${tinta}33` : `${tinta}e6`;
  }

  /* ── El respaldo quieto ────────────────────────────────────────────────────
     Donde no hay 3D, la escena era una pantalla negra con una frase. Aquí se
     dibuja la misma constelación —los mismos aforismos, las mismas relaciones,
     las mismas tintas y el mismo sendero encendido— quieta y en SVG: sin
     WebGL, sin librería y sin un solo fotograma de animación.

     Se calcula una sola vez, cuando se enciende el respaldo, y en píxeles de
     pantalla en vez de en un `viewBox` estirado: así las bolas son redondas y
     saber qué aforismo hay bajo el dedo es una resta. */
  let anchoPlano = $state(0);
  let altoPlano = $state(0);
  /* El hueco libre se mide, no se adivina: el rótulo ocupa una línea en ancho y
     tres en un móvil, y con un margen fijo el dibujo acababa detrás de la
     última («…PARA LEERLO» encima de una isla de aforismos). */
  let rotuloEl = $state<HTMLElement>();
  let altoRotulo = $state(0);
  let altoRespuesta = $state(0);

  /* El plano no es solo el respaldo de quien no tiene WebGL: es el primer
     estado de la vista para todo el mundo, mientras el 3D espera un hueco. */
  const sitios2d = $derived.by(() =>
    (sinWebgl || !tresDeVerdad) && grafo.nodos.length ? plano2dRecordado(grafo.nodos, grafo.aristas) : null,
  );

  /** Las posiciones en píxeles, con el hueco que dejan libre el rótulo de
   *  arriba y la respuesta de abajo: el dibujo no se mete debajo del texto. */
  const puntos2d = $derived.by(() => {
    const mapa = new Map<string, { x: number; y: number }>();
    if (!sitios2d || anchoPlano < 2 || altoPlano < 2) return mapa;
    const margenX = 26;
    const aire = 18;
    const arriba = Math.min((rotuloEl?.offsetTop ?? 0) + altoRotulo + aire, altoPlano * 0.45);
    const abajo = Math.min(altoRespuesta + aire, altoPlano * 0.3);
    const ancho = Math.max(10, anchoPlano - margenX * 2);
    const alto = Math.max(10, altoPlano - arriba - abajo);
    for (const [id, p] of sitios2d) {
      mapa.set(id, { x: margenX + p.x * ancho, y: arriba + p.y * alto });
    }
    return mapa;
  });

  let lienzoPlano = $state<HTMLCanvasElement>();

  /**
   * Dibuja la constelación plana. Se redibuja cuando cambia lo que se ve —el
   * sendero encendido, la ficha abierta, el tamaño del hueco— y nada más: no hay
   * bucle de pintado, porque un dibujo quieto no lo necesita.
   */
  $effect(() => {
    const lienzo = lienzoPlano;
    const puntos = puntos2d;
    const encendidos = hilosDelCamino;
    const conSendero = camino.length > 1;
    if (!lienzo || !puntos.size || anchoPlano < 2 || altoPlano < 2) return;
    // Un dibujo de líneas finas sí agradece la densidad de la pantalla, pero no
    // más de dos: a 3× son nueve veces los píxeles por el mismo dibujo.
    const densidad = Math.min(window.devicePixelRatio || 1, 2);
    lienzo.width = Math.round(anchoPlano * densidad);
    lienzo.height = Math.round(altoPlano * densidad);
    lienzo.style.width = `${anchoPlano}px`;
    lienzo.style.height = `${altoPlano}px`;
    const pincel = lienzo.getContext('2d');
    if (!pincel) return;
    pincel.setTransform(densidad, 0, 0, densidad, 0, 0);
    pincel.clearRect(0, 0, anchoPlano, altoPlano);

    // Primero los hilos apagados, en un solo trazo; luego los del sendero, que
    // van encima y más gruesos. Dos trazos en vez de 332 cambios de pincel.
    pincel.lineWidth = 0.7;
    pincel.strokeStyle = conSendero ? 'rgba(201,188,160,.10)' : 'rgba(186,172,140,.5)';
    pincel.beginPath();
    for (const arista of grafo.aristas) {
      if (encendidos.has(clave(arista.a, arista.b))) continue;
      const p = puntos.get(arista.a);
      const q = puntos.get(arista.b);
      if (!p || !q) continue;
      pincel.moveTo(p.x, p.y);
      pincel.lineTo(q.x, q.y);
    }
    pincel.stroke();

    if (encendidos.size) {
      pincel.lineWidth = 2;
      pincel.strokeStyle = '#f6c763';
      pincel.beginPath();
      for (const arista of grafo.aristas) {
        if (!encendidos.has(clave(arista.a, arista.b))) continue;
        const p = puntos.get(arista.a);
        const q = puntos.get(arista.b);
        if (!p || !q) continue;
        pincel.moveTo(p.x, p.y);
        pincel.lineTo(q.x, q.y);
      }
      pincel.stroke();
    }

    for (const nodo of grafo.nodos) {
      const p = puntos.get(nodo.id);
      if (!p) continue;
      pincel.fillStyle = colorDeNodo(nodo);
      pincel.beginPath();
      pincel.arc(p.x, p.y, radio2d(nodo), 0, Math.PI * 2);
      pincel.fill();
    }
  });

  function radio2d(nodo: NodoSendero): number {
    const base = 2.2 + Math.sqrt(Math.min(nodo.grado, 14)) * 1.5;
    if (nodo.id === origen || nodo.id === destino) return base * 1.9;
    if (enCamino.has(nodo.id)) return base * 1.4;
    return nodo.id === abierta ? base * 1.6 : base;
  }

  /** El mismo dedo de 22 px que en la escena 3D: gana el aforismo más cercano
   *  al toque, no el que caiga justo debajo del píxel. */
  function alTocarPlano(e: PointerEvent) {
    const caja = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const x = e.clientX - caja.left;
    const y = e.clientY - caja.top;
    let elegido: NodoSendero | null = null;
    let mejor = RADIO_DEDO;
    for (const nodo of grafo.nodos) {
      const p = puntos2d.get(nodo.id);
      if (!p) continue;
      const lejos = Math.hypot(p.x - x, p.y - y) - radio2d(nodo);
      if (lejos < mejor) { mejor = lejos; elegido = nodo; }
    }
    if (elegido) abrir(elegido.id);
  }

  function tamanoDeNodo(nodo: any): number {
    const base = 1 + Math.min(nodo.grado, 14) * 0.9;
    if (nodo.id === origen || nodo.id === destino) return base * 6;
    if (enCamino.has(nodo.id)) return base * 2.6;
    return nodo.id === abierta ? base * 3.4 : base;
  }

  function colorDeHilo(hilo: any): string {
    if (hilosDelCamino.has(clave(idDe(hilo.source), idDe(hilo.target)))) return '#f6c763';
    return camino.length > 1 ? 'rgba(201,188,160,.10)' : 'rgba(186,172,140,.55)';
  }

  /**
   * El grosor de un hilo. Un hilo con grosor es un cilindro: geometría propia,
   * seis gajos, que hay que construir. Trescientos treinta y dos cilindros son
   * la mitad del coste de levantar la escena (medido a 390 con la CPU a 1/4:
   * una tarea de 350 a 550 ms, y la física dentro de ella cuesta 0,2 ms el
   * paso, así que lo que pesa es construir cuerpos).
   *
   * En móvil, un hilo de fondo mide un píxel en pantalla: pedirle un cilindro
   * de seis gajos para que se vea igual que una línea es pagar por nada. Los de
   * fondo van como línea (grosor 0, que en la librería es una línea de un píxel
   * a cualquier distancia) y el sendero encendido sigue siendo un cilindro
   * grueso: así el contraste entre el camino y el resto es incluso mayor.
   */
  function anchoDeHilo(hilo: any): number {
    const delCamino = hilosDelCamino.has(clave(idDe(hilo.source), idDe(hilo.target)));
    if (delCamino) return 3.2;
    return enMovil ? 0 : 0.8;
  }

  /** Vuelve a pedirle a la escena que relea los colores y los tamaños. */
  function repintar() {
    if (!fg) return;
    fg.nodeColor(fg.nodeColor())
      .nodeVal(fg.nodeVal())
      .linkColor(fg.linkColor())
      .linkWidth(fg.linkWidth())
      .linkDirectionalParticles(fg.linkDirectionalParticles());
    // Quien pinta no es siempre el mismo: con la escena quieta («a demanda»)
    // basta despertarla un momento, pero en cuanto hay un sendero encendido
    // `despertar()` no hace nada —esa escena se pinta seguida— y el lienzo se
    // quedaba con el fotograma viejo: a 390 elegías los dos aforismos, la
    // respuesta decía «Sendero: 4 pasos» y el camino no se encendía hasta que
    // tocabas la pantalla. Aquí se elige el que toca.
    if (aDemanda()) despertar();
    else pintarSeguido();
  }

  /**
   * Mira un punto desde donde ya está la cámara, a la distancia pedida: así el
   * vuelo conserva el ángulo que el visitante había girado y no da un tumbo.
   */
  function mirarDesdeDonde(centro: { x: number; y: number; z: number }, distancia: number, ms = 900) {
    const camara = fg.cameraPosition();
    let dx = camara.x - centro.x;
    let dy = camara.y - centro.y;
    let dz = camara.z - centro.z;
    let largo = Math.hypot(dx, dy, dz);
    if (largo < 1) { dx = 0; dy = 0; dz = 1; largo = 1; }
    fg.cameraPosition(
      {
        x: centro.x + (dx / largo) * distancia,
        y: centro.y + (dy / largo) * distancia,
        z: centro.z + (dz / largo) * distancia,
      },
      centro,
      sinMovimiento ? 0 : ms,
    );
    despertar();
  }

  /**
   * Mirar el sendero de lado, nunca de punta.
   *
   * Si la cámara se queda donde estaba, puede caer en la línea misma del
   * sendero: las dos puntas se superponen y lo que se ve es una bola tapando a
   * la otra, sin camino. Se le quita a la mirada de ahora la parte que va a lo
   * largo del sendero y queda la perpendicular más cercana: el camino se abre
   * de lado y se mueve lo mínimo desde donde estaba mirando.
   */
  function mirarDeLado(
    centro: { x: number; y: number; z: number },
    eje: { x: number; y: number; z: number },
    distancia: number,
    ms = 900,
    /** Cuánto se mira por encima del centro: baja lo mirado en la pantalla. */
    subir = 0,
  ) {
    const camara = fg.cameraPosition();
    const largoEje = Math.hypot(eje.x, eje.y, eje.z) || 1;
    const ex = eje.x / largoEje, ey = eje.y / largoEje, ez = eje.z / largoEje;
    let vx = camara.x - centro.x, vy = camara.y - centro.y, vz = camara.z - centro.z;
    const aLoLargo = vx * ex + vy * ey + vz * ez;
    vx -= aLoLargo * ex; vy -= aLoLargo * ey; vz -= aLoLargo * ez;
    let largo = Math.hypot(vx, vy, vz);
    if (largo < 1) {
      // Estaba mirando justo por el eje del sendero: vale cualquier perpendicular.
      const otro = Math.abs(ex) < 0.9 ? { x: 1, y: 0, z: 0 } : { x: 0, y: 1, z: 0 };
      vx = ey * otro.z - ez * otro.y;
      vy = ez * otro.x - ex * otro.z;
      vz = ex * otro.y - ey * otro.x;
      largo = Math.hypot(vx, vy, vz) || 1;
    }
    fg.cameraPosition(
      {
        x: centro.x + (vx / largo) * distancia,
        y: centro.y + (vy / largo) * distancia,
        z: centro.z + (vz / largo) * distancia,
      },
      { x: centro.x, y: centro.y + subir, z: centro.z },
      sinMovimiento ? 0 : ms,
    );
    despertar();
  }

  /** La cámara vuela hasta el nodo tocado, como en la referencia. */
  function volarA(id: string) {
    const nodo = porIdFg.get(id);
    if (!fg || !nodo || typeof nodo.x !== 'number') return;
    // 220 unidades: lo bastante cerca para que el nodo mande en el encuadre y lo
    // bastante lejos para no meterse dentro de la nube (a 110 se veían bolas
    // gigantes de los nodos que quedaban entre medias).
    // 320 ms: los mismos que tarda la escena en encogerse para dejar sitio a la
    // hoja, para que el nodo no salga de cuadro y vuelva (`movimiento.md`).
    mirarDesdeDonde({ x: nodo.x, y: nodo.y, z: nodo.z }, 220, 320);
  }

  /** Encuadra el sendero entero: los dos extremos tienen que verse siempre. */
  function encuadrarCamino() {
    if (!fg || camino.length < 2) return;
    const pasos = camino.map((id) => porIdFg.get(id)).filter((n) => n && typeof n.x === 'number');
    if (pasos.length < 2) return;
    const centro = pasos.reduce(
      (suma, n) => ({ x: suma.x + n.x / pasos.length, y: suma.y + n.y / pasos.length, z: suma.z + n.z / pasos.length }),
      { x: 0, y: 0, z: 0 },
    );
    const radio = Math.max(...pasos.map((n) => Math.hypot(n.x - centro.x, n.y - centro.y, n.z - centro.z)));
    // Las dos puntas del sendero se dibujan seis veces más grandes que un
    // aforismo cualquiera. Si el camino es corto —dos vecinos— y la cámara se
    // acerca a lo que mide el camino, las dos bolas llenan la pantalla y se
    // tapan entre ellas: se veía una sola esfera verde. El suelo de distancia
    // deja sitio a las dos puntas y al hilo que las une.
    const punta = pasos[0];
    const cola = pasos[pasos.length - 1];
    // Una pantalla de móvil es estrecha: el campo de visión que manda es el
    // horizontal, y un sendero que cruza en diagonal se salía por la esquina
    // (medido a 390 con cc-001 → cc-030: la punta «desde» quedaba cortada
    // detrás de la línea de respuesta). La cámara se aparta un tercio más.
    const sitio = enMovil ? 1.55 : 1;
    const distancia = Math.max(430, radio * 2.6) * sitio;
    // A 390 el centro de la pantalla no es el centro del hueco libre: arriba
    // está el rótulo con la pista y abajo la línea de respuesta con la leyenda.
    // Se mira un poco por encima del sendero para que el camino caiga en medio
    // de lo que queda; si no, la punta de arriba se enredaba con la pista.
    mirarDeLado(
      centro,
      { x: cola.x - punta.x, y: cola.y - punta.y, z: cola.z - punta.z },
      distancia,
      900,
      enMovil ? distancia * 0.06 : 0,
    );
  }

  /**
   * Hay dos motivos para no pintar a todas horas: que el visitante haya pedido
   * menos movimiento, o que la máquina no dé (una tableta vieja, un portátil sin
   * tarjeta). En los dos casos la escena se queda quieta —entera, con su 3D— y
   * solo se pinta cuando algo cambia o cuando se la toca.
   */
  /*
   * Y hay un tercero: el móvil. Pintar esta constelación —doscientas esferas y
   * trescientos hilos, 433 órdenes de dibujo— cuesta unos 50 ms por fotograma en
   * un teléfono de gama media (medido a 390 con la CPU a 1/4: 17 fotogramas por
   * segundo girando sola). Un giro a 17 fps no es una constelación que gira: es
   * una constelación que tirita, y encima se lleva el hilo que necesita el dedo
   * para bajar por la página. Así que en móvil la constelación está quieta —
   * entera, con su 3D y sus luces— y se mueve cuando se la toca: el dedo la
   * gira, el toque vuela al nodo, y el botón «Girar» la pone a girar si alguien
   * lo quiere. Con un sendero encendido sí se pinta seguido, porque entonces hay
   * luz corriendo por los hilos y eso es lo que se ha venido a ver.
   */
  const aDemanda = () => sinMovimiento || flojo || (enMovil && camino.length < 2);

  function despertar() {
    if (!fg || !aDemanda()) return;
    // Si el dedo que está encima va hacia abajo, el gesto es de la página: no
    // se pinta aunque la cámara avise de un cambio (el control de órbita manda
    // ese aviso con el último movimiento antes de soltarlo).
    if (gestoDeLaPagina || rodando) return;
    // `pintando` es la cerradura: despertar a una escena despierta solo alarga
    // la siesta. Sin ella, el aviso «la cámara ha cambiado» del control de
    // órbita vuelve a llamar aquí dentro del propio pintado y se come la pila.
    if (!pintando) {
      pintando = true;
      fg.resumeAnimation();
    }
    clearTimeout(siesta);
    // La siesta se echa en cuanto nadie toca. En móvil la escena no vuela a
    // ningún sitio (el encuadre es instantáneo) y la inercia del dedo dura medio
    // segundo: seguir pintando 1,4 s eran veinte fotogramas de 50 ms cobrados a
    // cambio de nada. Cada aviso de la cámara vuelve a armar este reloj, así que
    // mientras algo se mueva, se pinta.
    siesta = window.setTimeout(() => dormir(), enMovil ? 420 : 1400);
  }

  function dormir() {
    pintando = false;
    clearTimeout(siesta);
    fg?.pauseAnimation();
  }

  /** Pintar seguido: girando, con un sendero encendido o en una máquina que da. */
  function pintarSeguido() {
    if (!fg || gestoDeLaPagina) return;
    clearTimeout(siesta);
    pintando = true;
    fg.resumeAnimation();
  }

  /**
   * Mide los fotogramas de verdad durante kilo y medio de segundo. Si no llegan
   * a diez por segundo, esta máquina no puede con el giro continuo: se apaga el
   * giro y se pasa a pintar bajo demanda. Es el respaldo quieto que pedía el
   * encargo, decidido con una medida y no de oído.
   */
  function vigilarFluidez() {
    if (!fg || sinMovimiento) return;
    const antes = fg.renderer().info.render.frame;
    const reloj = performance.now();
    window.setTimeout(() => {
      if (!fg) return;
      const pintados = fg.renderer().info.render.frame - antes;
      const segundos = (performance.now() - reloj) / 1000;
      if (pintados / segundos >= 24) return;
      flojo = true;
      girando = false;
      const mandos: any = fg.controls();
      if (mandos) mandos.autoRotate = false;
      fg.linkDirectionalParticles(0);
      // No se para en seco: si en ese momento la cámara está volando a un nodo,
      // cortarle el pintado la deja a medio camino y el nodo tocado se queda
      // fuera de cuadro. Se le da la siesta de `despertar()` y luego para.
      despertar();
    }, 1500);
  }

  /**
   * ¿Esta máquina sabe pintar en 3D? La pregunta barata, para decidir pronto si
   * vale la pena bajarse la librería: que exista el constructor.
   */
  const hayWebgl = (): boolean =>
    'WebGL2RenderingContext' in window || 'WebGLRenderingContext' in window;

  /**
   * La pregunta cara, la de verdad: ¿da esta máquina un contexto? El
   * constructor existe en navegadores que luego no pintan nada (3D apagado por
   * ajuste, una tarjeta sin memoria, los dieciséis contextos del navegador ya
   * repartidos). Dejar que lo descubriera la librería costaba un error de
   * consola que no es nuestro y que no se puede atrapar —`THREE.WebGLRenderer:
   * Error creating WebGL context.`, escrito con `console.error` dentro de
   * three—, y la entrega pide 0 errores.
   *
   * Cuesta 89 ms en una máquina sin tarjeta gráfica (medido a 390 con la CPU a
   * 1/4) y por eso se pregunta una sola vez y justo antes de levantar la
   * escena: donde responde que sí, esos 89 ms van delante de los 300–550 de
   * construirla; donde responde que no, ahorran la construcción entera. El
   * contexto de prueba se devuelve en el acto para no quedarse con uno de los
   * dieciséis.
   */
  function daContexto3d(): boolean {
    // La respuesta no cambia durante la visita y la pregunta cuesta 98 ms
    // (perfil del hilo a 390 con la CPU a 1/4): se guarda, y se hace pronto
    // —en el primer hueco tras montar, con la página todavía quieta— para que
    // no caiga en medio del gesto de quien ya está bajando.
    if (puede3d !== null) return puede3d;
    puede3d = probarContexto3d();
    return puede3d;
  }

  let puede3d: boolean | null = null;

  function probarContexto3d(): boolean {
    try {
      const prueba = document.createElement('canvas');
      prueba.width = prueba.height = 1;
      const ctx = (prueba.getContext('webgl2') ??
        prueba.getContext('webgl')) as WebGLRenderingContext | null;
      if (!ctx) return false;
      ctx.getExtension('WEBGL_lose_context')?.loseContext();
      return true;
    } catch {
      return false;
    }
  }

  /** La librería se pide a la vez que los datos: descargar 1,4 MB en serie
   *  detrás del `fetch` retrasaba la escena casi seis segundos en móvil lento. */
  let libreria: Promise<any> | null = null;

  async function levantarEscena() {
    if (!lienzo || fg) return;
    if (!daContexto3d()) throw new Error('sin contexto WebGL');
    const { default: ForceGraph3D } = await (libreria ?? import('3d-force-graph'));
    nodosFg = grafo.nodos.map((n) => ({ ...n }));
    porIdFg = new Map(nodosFg.map((n) => [n.id, n]));
    const hilos = grafo.aristas.map(({ a, b }) => ({ source: a, target: b }));

    // El suavizado de bordes es otra pasada entera del lienzo por fotograma. En
    // una pantalla de móvil, donde un aforismo mide seis píxeles, no se ve; lo
    // que se ve es el scroll (medido a 390: el lienzo suavizado se llevaba
    // 6,6 s de composición en seis segundos de scroll).
    fg = ForceGraph3D({ controlType: 'orbit', rendererConfig: { alpha: !enMovil, antialias: !enMovil } })(lienzo)
      // En móvil el lienzo es opaco y se pinta su propio cielo: una capa
      // translúcida del tamaño de la pantalla se mezcla con el degradado de
      // debajo en cada fotograma del scroll, y eso costaba el scroll entero
      // aunque la escena estuviera parada (medido a 390: 11 fps con el lienzo
      // transparente, 42 con el lienzo oculto). Opaco, el compositor lo tapa.
      .backgroundColor(enMovil ? '#13110c' : 'rgba(0,0,0,0)')
      .showNavInfo(false)
      .width((anchoEscena = lienzo.clientWidth))
      .height((altoEscena = lienzo.clientHeight))
      .nodeRelSize(3.4)
      // Doce gajos por esfera es una bola perfecta en una pantalla grande; en
      // móvil, con la esfera a seis píxeles, ocho gajos son la misma bola y
      // doscientas esferas menos de geometría que construir al levantarla.
      .nodeResolution(enMovil ? 8 : 12)
      .nodeOpacity(1)
      .nodeVal(tamanoDeNodo)
      .nodeColor(colorDeNodo)
      .nodeLabel((nodo: any) => resumen(nodo.texto, 72))
      .linkColor(colorDeHilo)
      .linkWidth(anchoDeHilo)
      .linkOpacity(0.85)
      .linkDirectionalParticles((hilo: any) =>
        !sinMovimiento && hilosDelCamino.has(clave(idDe(hilo.source), idDe(hilo.target))) ? 4 : 0,
      )
      .linkDirectionalParticleWidth(1.5)
      .linkDirectionalParticleSpeed(0.006)
      .linkDirectionalParticleColor(() => '#fff0c4')
      // El toque no lo resuelve la librería: lo resuelve `escucharToques`, que
      // admite el ancho de un dedo en vez de exigir el píxel exacto de la esfera.
      .enableNodeDrag(false)
      // En una pantalla de dedo no hay «pasar por encima»: no hay rótulo al
      // vuelo que mostrar, y sin embargo la librería lanzaba un rayo contra las
      // 534 mallas de la escena en cada fotograma, con su medida de la caja del
      // lienzo, para saber qué habría debajo del ratón que no existe. Apagado en
      // móvil: el toque lo resuelve `escucharToques` por proyección. En
      // escritorio se queda, que es donde el rótulo al vuelo se ve.
      .enablePointerInteraction(!enMovil)
      // La física, de una vez o a plazos según la máquina. En escritorio se
      // resuelve de golpe antes de pintar y la constelación aparece ya formada.
      // En móvil esos setenta pasos de golpe son un fotograma de 768 ms, y
      // darlos dentro del bucle de pintado son setenta fotogramas de 50 ms
      // (los dos, medidos a 390): se dan a plazos y **sin pintar**, en
      // `asentarLaConstelacion()`, y la escena aparece cuando ya está formada.
      .warmupTicks(enMovil ? 0 : 70)
      .cooldownTicks(enMovil ? PASOS_FISICA : 0)
      .graphData({ nodes: nodosFg, links: hilos });

    // Pintar a 2× en una pantalla de móvil es el doble de píxeles por fotograma
    // para una escena de esferas, donde no se nota: en móvil, uno a uno; en
    // escritorio se topa en 1,5.
    fg.renderer().setPixelRatio(enMovil ? 1 : Math.min(window.devicePixelRatio || 1, 1.5));

    // El dedo que sube y baja es de la página. El control de órbita de three le
    // pone `touch-action: none` a su propio lienzo al nacer, y eso se comía el
    // gesto entero: en móvil, con la constelación a pantalla completa, el dedo
    // giraba la escena y la página NO bajaba (medido a 390: cuatro gestos de
    // scroll seguidos = 0 px de página y 120 fotogramas de giro). Devuelto a
    // `pan-y`: el gesto vertical baja la página, el de lado gira la escena y el
    // pellizco sigue acercando, que es lo que promete la pista.
    fg.renderer().domElement.style.touchAction = 'pan-y';

    quitarToques = escucharToques();

    // Asa de desarrollo: las comprobaciones automáticas necesitan saber dónde cae
    // cada nodo en pantalla para tocarlo de verdad. No viaja al build.
    if (import.meta.env.DEV) (window as any).__sendero = fg;

    const mandos: any = fg.controls();
    mandos.enableDamping = true;
    mandos.dampingFactor = 0.12;
    mandos.rotateSpeed = 0.7;
    mandos.zoomSpeed = 0.8;
    mandos.minDistance = 40;
    mandos.maxDistance = 1400;
    // Con ratón, la rueda NO se queda la página: acercar es Ctrl/⌘ + rueda (como
    // en un mapa incrustado). Con el dedo sí manda el pellizco, y el gesto
    // vertical de un dedo lo sigue teniendo la página (`touch-action: pan-y`).
    mandos.enableZoom = window.matchMedia('(pointer: coarse)').matches;
    mandos.autoRotateSpeed = 0.5;
    mandos.autoRotate = girando && !sinMovimiento;
    // Mientras la cámara se mueva —el dedo girándola, la inercia, un vuelo a un
    // nodo— la escena se pinta. Es lo que hace que «quieta hasta que la tocas»
    // no se note: el que la toca la ve moverse, y en cuanto suelta, se para.
    mandos.addEventListener('change', despertar);

    fg.onEngineStop(() => {
      // El encuadre de bienvenida solo manda si nadie ha tocado nada: si ya hay
      // un sendero o una ficha abierta, la cámara está donde la han puesto.
      // En móvil la constelación entra de una (0 ms) en vez de volar 800 ms:
      // cada fotograma de ese vuelo cuesta aquí 50 ms y el vuelo se ve a saltos.
      if (!origen && !destino && !abierta) fg?.zoomToFit(sinMovimiento || enMovil ? 0 : 800, 70);
      else if (camino.length > 1) encuadrarCamino();
      // Formada ya la constelación, el que pinta bajo demanda se para aquí: la
      // escena queda a la vista, quieta, y el siguiente dedo la despierta.
      if (aDemanda()) despertar();
      else vigilarFluidez();
    });
    // Con «menos movimiento» la escena se para en cuanto está formada (en
    // `onEngineStop`, cuando ya hay algo que mirar): no se quita la obra, se
    // quita el movimiento.

    if (enMovil) await asentarLaConstelacion();
    // La constelación ya está en pie, por el camino que haya sido: el rótulo
    // deja de decir que la está levantando. Decirlo solo al final de
    // `asentarLaConstelacion()` dejaba el aviso puesto para siempre en
    // escritorio (donde no se llama) y también en móvil si la malla no estaba
    // donde se la buscaba, y se veía: «Levantando la constelación…» encima de
    // una constelación levantada.
    montando = false;
    // Y el relevo: la constelación plana no se quita hasta que la de 3D ha
    // pintado un fotograma de verdad. Quitarla al crear la escena dejaba un
    // cielo negro durante el parpadeo que tarda el primer pintado (hasta 230 ms
    // en esta máquina sin tarjeta gráfica).
    await unFotogramaPintado();
    tresDeVerdad = true;
  }

  /**
   * Espera a que el lienzo 3D haya pintado una vez. Se pregunta al contador de
   * fotogramas de three, no al reloj: en modo «a demanda» el bucle puede tardar
   * en arrancar, y con un plazo de gracia para no quedarse colgado si no pinta.
   */
  async function unFotogramaPintado(): Promise<void> {
    if (!fg) return;
    const antes = fg.renderer().info.render.frame;
    despertar();
    const plazo = performance.now() + 1200;
    while (fg && fg.renderer().info.render.frame === antes && performance.now() < plazo)
      await new Promise((listo) => requestAnimationFrame(listo));
  }

  /** Pasos de física que necesita el corpus para dejar de moverse. */
  const PASOS_FISICA = 70;

  /**
   * La constelación se asienta a plazos y a oscuras: se le dan pasos de física
   * hasta gastar 24 ms de hilo, se devuelve el hilo al dedo, y vuelta a empezar.
   * Pintar no se pinta hasta el final, porque pintar es lo caro (50 ms el
   * fotograma en esta máquina sin tarjeta gráfica): el precio de verla formarse
   * eran setenta fotogramas lentos. Mientras tanto, el rótulo dice la verdad —
   * «Levantando la constelación…»— y al terminar la escena entra ya formada.
   */
  async function asentarLaConstelacion() {
    const malla: any = fg?.scene().children.find((o: any) => typeof o.tickFrame === 'function');
    if (!malla) return;
    montando = true;
    dormir();
    for (let pasos = 0; pasos < PASOS_FISICA && fg; ) {
      // Si el dedo está bajando la página, la física espera: un plazo de 24 ms
      // era un fotograma de 80 ms a 1/4 de CPU, y el scroll se notaba a saltos
      // (medido a 390: 54 fotogramas por encima de 50 ms mientras se asentaba).
      // Ocho milisegundos por plazo caben en un fotograma de 60 Hz con sitio
      // de sobra; asentarse tarda unos pasos más y nadie lo nota, porque es a
      // oscuras.
      if (rodando) await new Promise<void>((sigue) => cuandoPareLaPagina(sigue));
      if (!fg) break;
      const hasta = performance.now() + 8;
      do { malla.tickFrame(); pasos++; } while (pasos < PASOS_FISICA && performance.now() < hasta);
      await new Promise((listo) => requestAnimationFrame(listo));
    }
    montando = false;
    despertar();
  }

  /**
   * Lo que pesa, cuando la página esté quieta. Mientras se baja, el hilo es del
   * dedo: ni se levanta la escena ni se asienta la física ni se pinta. En cuanto
   * para —180 ms sin scroll— se sigue por donde se iba.
   */
  function cuandoPareLaPagina(fn: () => void) {
    if (!rodando) { fn(); return; }
    const anterior = enEspera;
    enEspera = () => { anterior?.(); fn(); };
  }

  /**
   * Mientras la página se mueve, la escena no se pinta. Nadie mira girar una
   * constelación mientras baja a leer, y cada fotograma de lienzo compite con el
   * scroll por el mismo hilo (medido a 390: 11,8 fotogramas por segundo con la
   * escena pintando, 60 sin ella). Al parar el dedo, vuelve a pintarse.
   */
  /**
   * Un dedo apoyado que se mueve, o un ratón arrastrando con el botón apretado:
   * el visitante está haciendo algo con la mano y el hilo es suyo, aunque la
   * página no llegue a moverse ni un píxel. Pasa de verdad en esta vista, que
   * ocupa la pantalla entera: hay gestos que no mueven la página (y entonces no
   * hay un solo evento de scroll ni de `touchmove` que avise) y durante los
   * cuales montar la escena o llenar las listas son tirones de 350 y de 100 ms.
   * Un ratón que solo pasea por encima no cuenta: ahí nadie está pidiendo nada.
   */
  function alArrastrar(e: PointerEvent) {
    if (e.pointerType === 'touch' || e.buttons !== 0) alMoverLaPagina();
  }

  /**
   * Media segundo de calma antes de la única tarea que no se puede partir:
   * levantar la escena. Construir los cuerpos de la constelación es una tarea
   * de 300 a 550 ms (medido a 390 con la CPU a 1/4) y no hay manera de darla a
   * trozos: la librería construye lo visible de una vez, y ponerlo por lotes
   * sale peor, porque cada lote vuelve a repasar las cuentas de todo lo ya
   * puesto (probado: tandas de 80 ms, trece veces, en vez de una de 350).
   *
   * Así que lo que se decide es *cuándo*: no mientras la mano del visitante
   * esté ocupada, y no justo después —los 180 ms que bastan para volver a
   * pintar no bastan aquí, porque un gesto largo tiene pausas más cortas que
   * eso y la tarea se colaba en una de ellas—. Con la mano quieta medio
   * segundo, la escena se levanta. Mientras espera, el rótulo lo dice.
   *
   * Y con un tope, porque la calma puede no llegar: quien baja la página sin
   * parar —o un gesto sintético de prueba, que no para en 6 s— dejaba la
   * constelación sin levantar y el rótulo «Levantando la constelación…»
   * puesto para siempre. A los `tope` ms se levanta igual: un tirón de una vez
   * es mucho menos malo que una vista que no llega.
   */
  function cuandoHayaCalma(ms: number, fn: () => void, tope = ms * 4) {
    const plazo = performance.now() + tope;
    const mirar = () => {
      if (!vivoEnPantalla) return;
      const ahora = performance.now();
      const falta = Math.min(ms - (ahora - ultimoMovimiento), plazo - ahora);
      if (falta > 0) { window.setTimeout(mirar, falta); return; }
      fn();
    };
    mirar();
  }

  function alMoverLaPagina() {
    // El dedo que está girando la constelación manda `touchmove` como cualquier
    // otro, pero no está moviendo la página: ahí sí se pinta, es lo que ha
    // pedido.
    if (gestoDelGrafo) return;
    ultimoMovimiento = performance.now();
    if (!rodando) { rodando = true; if (fg) dormir(); }
    clearTimeout(finDeScroll);
    finDeScroll = window.setTimeout(() => {
      rodando = false;
      const pendiente = enEspera;
      enEspera = null;
      pendiente?.();
      if (!fg) return;
      // Fuera de pantalla no se vuelve a pintar: la constelación queda arriba y
      // quien ha bajado está leyendo otra cosa. Sin esta línea, cada pausa del
      // gesto encendía un lienzo que ya nadie veía.
      if (!aLaVista) return;
      // Y en modo «a demanda» —menos movimiento, máquina sin tarjeta gráfica, o
      // la constelación quieta del móvil— que la página pare no es una demanda:
      // nada ha cambiado mientras se bajaba, el lienzo sigue con su último
      // fotograma puesto y repintarlo costaba un tirón por nada. Se pinta cuando
      // alguien la toca, cuando la cámara vuela a un nodo o cuando cambia de
      // tamaño, que son los tres sitios que llaman a `despertar()`.
      if (aDemanda()) return;
      pintarSeguido();
    }, ESPERA_PARA_PINTAR);
  }

  onMount(() => {
    sinMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    enMovil = window.matchMedia('(pointer: coarse)').matches || window.innerWidth < 768;
    // En móvil el giro automático no viene puesto (ver `aDemanda`): está el botón.
    if (sinMovimiento || enMovil) girando = false;
    let vivo = true;
    let mirando: IntersectionObserver | null = null;
    let midiendo: ResizeObserver | null = null;

    // La librería: la que ya pidió la página al leerse, o esta.
    libreria = (globalThis as any).__senderoLibreria ?? null;
    if (!libreria && hayWebgl()) libreria = import('3d-force-graph');
    // Y la pregunta cara —¿da esta máquina un contexto?— se hace aquí, en el
    // primer hueco del hilo, mientras los datos viajan y la página sigue
    // quieta. Hecha más tarde, dentro de `levantarEscena()`, eran 98 ms
    // pegados al gesto de quien ya iba bajando.
    if (hayWebgl())
      (window.requestIdleCallback ?? ((f: any) => window.setTimeout(f, 200)))(() => daContexto3d(), {
        timeout: 800,
      });

    // Saber si la mano del visitante está ocupada se apunta desde el primer
    // momento, no cuando llegan los datos. Apuntándolo después había una
    // rendija: si los datos llegaban **en medio** de un gesto, nadie había
    // visto empezar ese gesto, así que la escena se creía la página quieta y se
    // montaba encima de la mano (medido a 390 con la CPU a 1/4: una tarea de
    // 437 ms justo dentro del gesto).
    window.addEventListener('scroll', alMoverLaPagina, { passive: true });
    window.addEventListener('touchmove', alMoverLaPagina, { passive: true });
    window.addEventListener('pointermove', alArrastrar, { passive: true });

    (async () => {
      try {
        // Las dos llamadas salen juntas, pero la constelación solo espera a la
        // suya. El corpus son 230 KB de citas enteras que únicamente hacen falta
        // cuando se abre una ficha, y esperarlo retrasaba la escena: con el
        // backend a un segundo por llamada, la constelación salía cuando el
        // visitante ya iba bajando y el trabajo de levantarla caía dentro de su
        // gesto. Ahora sale con su grafo y las fichas se llenan al llegar.
        const esperaCorpus = traerCorpus();
        const delBackend = await traerGrafo();
        if (!vivo) return;
        // Solo se espera al corpus si el backend no dio grafo: entonces es la
        // única manera de dibujar algo (`desdeCorpus`).
        const corpus = delBackend ? null : await esperaCorpus;
        esperaCorpus.then((entradas) => {
          if (vivo && entradas) fichas = new Map(entradas.map((e) => [e.id, e]));
        });
        const respuesta = delBackend ?? (corpus?.length ? desdeCorpus(corpus) : null);
        if (!respuesta) throw new Error('sin grafo');
        grafo = construirGrafo(respuesta, lang);
        if (!vivo) return;
        restaurarDeLaDireccion();
        cargando = false;
        if (!hayWebgl()) { sinWebgl = true; return; }
        // La constelación se levanta en cuanto hay datos, sin esperar hueco: es
        // la protagonista de la página y lo único que hay que mirar mientras se
        // monta. Esperando a `requestIdleCallback` se levantaba más tarde, justo
        // cuando el visitante ya estaba bajando, y los doscientos cuerpos de la
        // escena se construían **mientras** se hacía scroll (medido a 390: 20
        // tareas largas durante el scroll, de 73 a 399 ms). Construida antes, el
        // scroll encuentra la escena hecha y quieta.
        //
        // Con una excepción: si el visitante ya va bajando cuando llegan los
        // datos, el hilo es suyo. Construir doscientos cuerpos y pintarlos la
        // primera vez son 231 ms de hilo de una sentada (medido a 390 con la CPU
        // a 1/4, en la traza: `FireAnimationFrame` dentro de `3d-force-graph`), y
        // en medio de un gesto eso es la página dando un tirón. Se espera a que
        // la mano pare —medio segundo de calma, ver `cuandoHayaCalma`— y
        // entonces se levanta.
        //
        // En una pantalla de dedo el aviso que llega antes no es el scroll: es
        // el propio dedo. Un dedo arrastrando sobre una vista a pantalla
        // completa puede no mover la página ni un píxel (y entonces no hay un
        // solo evento de scroll que avise) y sin embargo está pidiendo algo:
        // ese hilo es suyo. Quien lo apunta son las tres escuchas de arriba.
        //
        // Y la espera puede ser larga sin que falte nada, porque mientras tanto
        // la constelación ya está en pantalla, plana y tocable: antes el tope
        // eran dos segundos porque detrás del rótulo no había nada que mirar y
        // «un tirón una vez» salía mejor que «una vista que no llega». Con el
        // plano puesto, el tirón no hace falta: el 3D entra en el primer hueco
        // de verdad, y el tope de diez segundos solo está para que una mano que
        // no para nunca acabe viéndolo igual.
        montando = true;
        // Si la máquina tiene el constructor de WebGL pero no puede dar un
        // contexto (una tarjeta sin memoria, dieciséis lienzos ya abiertos), lo
        // dice aquí: se enciende el respaldo sin WebGL y no el cartel de error.
        cuandoHayaCalma(
          500,
          () => {
            if (vivo)
              levantarEscena().catch(() => {
                if (!vivo) return;
                sinWebgl = true;
                // Y el rótulo deja de decir que la levanta: no hay nada
                // levantándose. Decía «Levantando la constelación…» encima de una
                // pantalla negra y vacía, para siempre.
                montando = false;
              });
          },
          10000,
        );

        // Fuera de pantalla no se dibuja: el grafo no gasta batería mientras se
        // lee el sendero más abajo.
        if (escena && 'IntersectionObserver' in window) {
          mirando = new IntersectionObserver((entradas) => {
            for (const entrada of entradas) {
              if (!fg) continue;
              // Basta con que la escena se vaya quedando atrás para dejar de
              // pintarla: mientras se lee el sendero, el 3D no cuesta nada.
              aLaVista = entrada.intersectionRatio > 0.25;
              if (aLaVista && !aDemanda() && !rodando) pintarSeguido();
              else if (!aLaVista) dormir();
              // Y cuando ya no se ve nada de ella, el lienzo se esconde: aunque
              // no se pinte, componer una capa de ese tamaño en cada fotograma
              // costaba el scroll entero (medido: 4,3 fps → 50 con el lienzo
              // oculto, en el build de producción con la CPU a 1/4).
              dormido = entrada.intersectionRatio <= 0.02;
            }
          }, { threshold: [0, 0.15, 0.25, 0.4] });
          mirando.observe(escena);
        }
        if (lienzo && 'ResizeObserver' in window) {
          // Cambiar de tamaño no es gratis: cada `width()` y cada `height()`
          // rehacen el búfer de dibujo de WebGL (`setSize`), y en el perfil del
          // hilo a 390 eso era lo más caro de la librería durante el scroll
          // —100 ms en `setSize` más 122 ms en lo que arrastra—. Y durante el
          // scroll el alto cambia solo: en un móvil la barra del navegador se
          // esconde y vuelve, y cada centímetro de barra era otro búfer.
          //
          // Así que se espera a que el tamaño se quede quieto (150 ms), se
          // ignora el aviso que no cambia nada, y se toca solo el lado que
          // cambió. La ficha, que encoge la escena, entra en 240 ms: el
          // encuadre nuevo llega dentro de su propia entrada.
          let apuntado = 0;
          midiendo = new ResizeObserver(() => {
            if (!fg || !lienzo || apuntado) return;
            apuntado = window.setTimeout(() => {
              apuntado = 0;
              if (!fg || !lienzo) return;
              const ancho = lienzo.clientWidth;
              const alto = lienzo.clientHeight;
              if (ancho === anchoEscena && alto === altoEscena) return;
              if (ancho !== anchoEscena) fg.width(ancho);
              if (alto !== altoEscena) fg.height(alto);
              anchoEscena = ancho;
              altoEscena = alto;
              // Cambiar de tamaño vacía el lienzo. Si la escena está en modo «a
              // demanda» (máquina lenta o menos movimiento) nadie vuelve a
              // pintarla y el grafo se queda negro justo al abrir la ficha, que
              // es cuando la escena se encoge. Se despierta para repintar.
              despertar();
            }, 150);
          });
          midiendo.observe(lienzo);
        }
      } catch {
        if (!vivo) return;
        fallo = true;
        cargando = false;
      }
    })();

    return () => {
      vivo = false;
      vivoEnPantalla = false;
      enEspera = null;
      window.removeEventListener('scroll', alMoverLaPagina);
      window.removeEventListener('touchmove', alMoverLaPagina);
      window.removeEventListener('pointermove', alArrastrar);
      clearTimeout(finDeScroll);
      mirando?.disconnect();
      midiendo?.disconnect();
      clearTimeout(siesta);
      clearTimeout(cruce);
      quitarToques?.();
      quitarToques = null;
      fg?._destructor?.();
      fg = null;
    };
  });

  // Cambia la selección: la escena se relee y el sendero se encuadra.
  $effect(() => {
    void origen; void destino;
    repintar();
    if (camino.length > 1) encuadrarCamino();
  });

  $effect(() => {
    void abierta;
    repintar();
  });

  $effect(() => {
    const mandos: any = fg?.controls?.();
    if (!mandos) return;
    mandos.autoRotate = girando && !sinMovimiento;
    // Si lo piden girando, se pinta aunque la máquina sea lenta: es su decisión.
    if (girando) pintarSeguido();
    else if (aDemanda()) dormir();
  });

  // La ficha se abre con el foco dentro: con teclado no hay que buscarla. Sin
  // robarle el scroll a nadie: de traer la escena se encarga `verLaEscena()`.
  $effect(() => {
    if (abierta && panel) panel.focus({ preventScroll: true });
  });

  /**
   * Rueda: sin Ctrl/⌘ la página baja, con Ctrl/⌘ la cámara se acerca.
   *
   * Va en la fase de captura y corta el evento ahí mismo, porque el control de
   * órbita de three escucha en el lienzo y hace `preventDefault()` por su cuenta:
   * la rueda se la quedaba el grafo y la página no bajaba (medido a 390: veinte
   * giros de rueda sobre la escena = dos eventos de scroll). Cortado en captura,
   * el control nunca la ve y el dedo sigue siendo de la página, que es lo que
   * dice la pista.
   */
  function alRodar(evento: WheelEvent) {
    if (!(evento.ctrlKey || evento.metaKey)) { evento.stopPropagation(); return; }
    if (!fg) return;
    evento.preventDefault();
    const camara = fg.cameraPosition();
    const centro: any = (fg.controls() as any)?.target ?? { x: 0, y: 0, z: 0 };
    const paso = evento.deltaY > 0 ? 1.14 : 0.88;
    fg.cameraPosition(
      {
        x: centro.x + (camara.x - centro.x) * paso,
        y: centro.y + (camara.y - centro.y) * paso,
        z: centro.z + (camara.z - centro.z) * paso,
      },
      centro,
      0,
    );
    despertar();
  }

  function alTeclado(evento: KeyboardEvent) {
    if (evento.key === 'Escape' && abierta) { limpiarFicha(); }
  }

  function limpiarFicha() {
    clearTimeout(cruce);
    cruzando = false;
    abierta = '';
    // El foco vuelve a quien abrió la carta. Si fue un toque en la
    // constelación (que no se tabula), al título de la escena: nunca al vacío.
    const destinoFoco = volverA?.isConnected ? volverA : tituloEl;
    volverA = null;
    void tick().then(() => destinoFoco?.focus({ preventScroll: true }));
  }

  /**
   * En móvil la carta se arrastra hacia abajo para cerrarla, como la lectura
   * de Sabiduría: sigue al dedo (solo `transform`) y, si no llega a 80 px,
   * vuelve a su sitio. Se agarra por la cabecera, que no hace scroll.
   */
  let agarre: { y: number; id: number } | null = null;
  function alAgarrar(e: PointerEvent) {
    if (e.pointerType === 'mouse' || (e.target as HTMLElement).closest('a,button') || !panel) return;
    if (window.matchMedia('(min-width: 48rem)').matches) return;
    agarre = { y: e.clientY, id: e.pointerId };
    arrastre = 0;
    try { (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId); } catch { /* sin captura, sigue igual */ }
  }
  function alArrastrarCarta(e: PointerEvent) {
    if (!agarre || e.pointerId !== agarre.id || !panel) return;
    arrastre = Math.max(0, e.clientY - agarre.y);
    panel.style.transform = `translateY(${arrastre}px)`;
  }
  function alSoltarCarta(e: PointerEvent) {
    if (!agarre || e.pointerId !== agarre.id || !panel) return;
    agarre = null;
    if (arrastre > 80) { limpiarFicha(); return; }
    const desde = arrastre;
    arrastre = 0;
    panel.style.transform = '';
    if (desde && !sinMovimiento) {
      panel.animate([{ transform: `translateY(${desde}px)` }, { transform: 'none' }], { duration: 240, easing: 'cubic-bezier(.2,.7,.2,1)' });
    }
  }

  /**
   * La curva del plan de movimiento, `cubic-bezier(.2,.7,.2,1)`, resuelta para
   * poder usar la misma en CSS (el lienzo) y en JS (la hoja). Se busca el
   * parámetro cuya abscisa vale `t` por bisección y se devuelve su ordenada.
   */
  function curva(t: number) {
    const abscisa = (s: number) => 3 * s * (1 - s) ** 2 * 0.2 + 3 * s ** 2 * (1 - s) * 0.2 + s ** 3;
    const ordenada = (s: number) => 3 * s * (1 - s) ** 2 * 0.7 + 3 * s ** 2 * (1 - s) * 1 + s ** 3;
    let bajo = 0;
    let alto = 1;
    let s = t;
    for (let i = 0; i < 18; i += 1) { s = (bajo + alto) / 2; if (abscisa(s) < t) bajo = s; else alto = s; }
    return ordenada(s);
  }

  /**
   * La hoja se posa, no se desliza desde fuera: 16 px a 390 y 12 px de lado en
   * ancho, los que hace falta para que se vea llegar. Con «menos movimiento»
   * solo cambia la opacidad y el contenido es el mismo (`movimiento.md`).
   */
  function hoja(_nodo: Element, { ms, espera, sale = false }: { ms: number; espera: number; sale?: boolean }) {
    if (sinMovimiento) return { duration: 120, delay: 0, css: (t: number) => `opacity:${t}` };
    const enAncho = window.matchMedia('(min-width: 48rem)').matches;
    const eje = enAncho ? 'X' : 'Y';
    // Si se cierra arrastrando, la carta sigue cayendo desde donde la soltó el
    // dedo, no salta a su sitio para luego irse.
    const desde = sale && !enAncho ? arrastre : 0;
    const salto = desde ? 160 : enAncho ? 12 : 16;
    return {
      duration: ms,
      delay: espera,
      easing: curva,
      css: (t: number, u: number) => `opacity:${t}; transform: translate${eje}(${desde + u * salto}px)`,
    };
  }
</script>

<svelte:window onkeydown={alTeclado} />

<section class="sendero" aria-labelledby="sendero-titulo" bind:this={caja}>
  <div class="sendero__escena" bind:this={escena}>
    <div
      class="sendero__lienzo"
      class:sendero__lienzo--ficha={Boolean(nodoAbierto)}
      class:sendero__lienzo--dormido={dormido}
      bind:this={lienzo}
      aria-hidden="true"
      onpointerdown={despertar}
      onwheelcapture={alRodar}
      ontouchstart={despertar}
    ></div>

    {#if sinWebgl || !tresDeVerdad}
      <!-- La constelación plana: el primer estado de la vista (y el único en un
           navegador sin WebGL). Como el lienzo 3D, se toca con el dedo y no se
           tabula: quien va con teclado tiene los dos desplegables de abajo y
           los vecinos de la ficha, que llevan a los mismos 202 aforismos. -->
      <div
        class="sendero__plano"
        class:sendero__plano--ficha={Boolean(nodoAbierto)}
        bind:clientWidth={anchoPlano}
        bind:clientHeight={altoPlano}
        onpointerup={alTocarPlano}
        aria-hidden="true"
      >
        <!-- Un lienzo 2D, no 534 elementos SVG: dibujar las 202 estrellas y sus
             332 hilos como nodos del documento era una tarea de 100 ms del
             runtime de Svelte (medido a 390 con la CPU a 1/4, en la traza de
             Chrome), y caía justo cuando llegan los datos, que es cuando el
             visitante ya está bajando. En un lienzo son 534 trazos de una vez,
             sin DOM que mantener. Se toca igual: quién hay bajo el dedo es una
             resta sobre `puntos2d`, no una pregunta al navegador. -->
        <canvas bind:this={lienzoPlano} aria-hidden="true"></canvas>
      </div>
    {/if}

    <div class="sendero__velo" class:sendero__velo--ficha={Boolean(nodoAbierto)} aria-hidden="true"></div>

    <header
      class="sendero__rotulo"
      class:sendero__rotulo--oculto={Boolean(nodoAbierto)}
      bind:this={rotuloEl}
      bind:clientHeight={altoRotulo}
    >
      <h1 id="sendero-titulo" tabindex="-1" bind:this={tituloEl}>{copia.titulo}</h1>
      <!-- La pista dice lo que se puede hacer *aquí*: sin 3D no se arrastra
           para girar ni se pellizca para acercar, y prometerlo era mentir. Y
           va en el rótulo, sobre papel limpio, no encima del dibujo. -->
      <p class="sendero__pista">
        {cargando
          ? copia.cargando
          : sinWebgl
            ? copia.sinWebgl
            : !tresDeVerdad
              ? copia.plana
              : copia.pista}
      </p>
    </header>

    <div
      class="sendero__respuesta"
      class:sendero__respuesta--ficha={Boolean(nodoAbierto)}
      bind:clientHeight={altoRespuesta}
    >
      <p class="sendero__cifra">
        <!-- Sin sendero no se dice «Sendero: sin sendero»: tartamudea. El
             rótulo aparece cuando hay algo que contar. -->
        {#if camino.length > 1}
          <strong>{copia.senderoCorto}:</strong> {copia.pasos(camino.length - 1)}
        {:else}
          <strong>{copia.sinSendero}</strong>
        {/if}
        <span class="sendero__sep">·</span>
        {copia.nodos} {grafo.nodos.length}
        <span class="sendero__sep">|</span>
        {copia.relaciones} {grafo.aristas.length}
      </p>
      <ul class="sendero__leyenda" aria-label={copia.leyenda}>
        <li><span class="muestra muestra--desde" aria-hidden="true"></span>{copia.leyendaDesde}</li>
        <li><span class="muestra muestra--hasta" aria-hidden="true"></span>{copia.leyendaHasta}</li>
        <li><span class="muestra muestra--paso" aria-hidden="true"></span>{copia.leyendaPaso}</li>
        <li><span class="muestra muestra--hilo" aria-hidden="true"></span>{copia.leyendaHilo}</li>
        <li><span class="muestra muestra--resto" aria-hidden="true"></span>{copia.leyendaResto}</li>
      </ul>
    </div>

    {#if !sinWebgl}
      <button
        type="button"
        class="sendero__giro"
        aria-pressed={girando}
        onclick={() => (girando = !girando)}
      >{copia.girar}</button>
    {/if}


    {#if nodoAbierto}
      {@const seccionLeida = rotuloSeccion(nodoAbierto.seccion, lang)}
      <!-- La carta: una página arrancada del volumen de su sección, la misma
           materia que la lectura de Sabiduría (papel, raya roja de margen,
           lomo del color del nodo). Flota sobre la noche sin pegarse a los
           bordes; en móvil es una hoja que se baja con el dedo. Es un diálogo
           no modal: el grafo sigue vivo detrás y Esc la cierra. -->
      <div
        class="sendero__ficha"
        role="dialog"
        aria-modal="false"
        aria-label={copia.ficha}
        tabindex="-1"
        style={`--lomo:${tintaDeSeccion(nodoAbierto.seccion)}`}
        bind:this={panel}
        in:hoja={{ ms: 240, espera: 80 }}
        out:hoja={{ ms: 200, espera: 0, sale: true }}
      >
        <!-- La cabecera no hace scroll: es por donde se agarra la carta. -->
        <div
          class="sendero__ficha-cabeza"
          role="presentation"
          onpointerdown={alAgarrar}
          onpointermove={alArrastrarCarta}
          onpointerup={alSoltarCarta}
          onpointercancel={alSoltarCarta}
        >
          <span class="sendero__asa" aria-hidden="true"></span>
          <span class="sendero__sello" aria-hidden="true">{seccionLeida.slice(0, 1).toLocaleUpperCase(lang)}</span>
          <p class="sendero__ficha-volumen">
            <span>{copia.volumen} · {seccionLeida}</span>
            <span class="sendero__ficha-folio">
              {nodoAbierto.idTexto} · {fichaAbierta?.level ? rotuloNivel(fichaAbierta.level, lang) : copia.sinNivel}
            </span>
          </p>
          <button
            type="button"
            class="sendero__cerrar"
            aria-label={copia.cerrar}
            title={copia.cerrar}
            onclick={limpiarFicha}
          >
            <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true" focusable="false">
              <path d="M4 4 L12 12 M12 4 L4 12" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </button>
        </div>
        <div class="sendero__ficha-cuerpo" class:sendero__ficha-cuerpo--cruza={cruzando}>
          <blockquote class="sendero__ficha-cita" class:sendero__ficha-cita--larga={nodoAbierto.texto.length > 140} lang={nodoAbierto.idiomaTexto}>{nodoAbierto.texto}</blockquote>
          {#if nodoAbierto.idiomaTexto !== lang}<p class="sendero__ficha-nota">{copia.sinTraducir}</p>{/if}
          {#if fichaAbierta?.teaches}
            <p class="sendero__ficha-glosa" lang={fichaAbierta.lang}>{fichaAbierta.teaches}</p>
          {/if}
          <div class="sendero__ficha-acciones">
            <button
              type="button"
              class="sendero__marcar"
              aria-pressed={origen === nodoAbierto.id}
              onclick={() => {
                origen = origen === nodoAbierto.id ? '' : nodoAbierto.id;
                eligiendo = origen ? 'destino' : 'origen';
              }}
            ><span class="muestra muestra--desde" aria-hidden="true"></span>{origen === nodoAbierto.id ? copia.esDesde : copia.desdeAqui}</button>
            <button
              type="button"
              class="sendero__marcar"
              aria-pressed={destino === nodoAbierto.id}
              onclick={() => {
                destino = destino === nodoAbierto.id ? '' : nodoAbierto.id;
                eligiendo = destino ? 'origen' : 'destino';
              }}
            ><span class="muestra muestra--hasta" aria-hidden="true"></span>{destino === nodoAbierto.id ? copia.esHasta : copia.hastaAqui}</button>
            <a class="sendero__ficha-enlace" href={`/${lang}/wisdom/${nodoAbierto.idTexto}/`}>{copia.verFicha} <span aria-hidden="true">→</span></a>
          </div>
          {#if vecinosAbiertos.length}
            <!-- El contador va en el rótulo de la lista y cuenta lo que hay
                 debajo: la ficha no dice un número que la lista no sostenga. -->
            <h2 class="sendero__ficha-titulo">
              {copia.vecinos} <span class="sendero__cuenta">{vecinosAbiertos.length}</span>
            </h2>
            <ul class="sendero__vecinos">
              {#each vecinosAbiertos as vecino (vecino.id)}
                <li>
                  <button type="button" onclick={() => abrir(vecino.id)}>
                    <span class="sendero__punto" style={`background:${tintaDeSeccion(vecino.seccion)}`} aria-hidden="true"></span>
                    <span class="sendero__vecino-texto">{resumen(vecino.texto, 70)}</span>
                    <span class="sendero__vecino-dato">{vecino.grado}</span>
                  </button>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    {/if}
  </div>

  {#snippet hueco(papel: 'origen' | 'destino', rotulo: string, id: string)}
    {@const nodo = porId.get(id)}
    <div class="sendero__hueco" class:sendero__hueco--activo={eligiendo === papel} data-papel={papel}>
      <button
        type="button"
        class="sendero__hueco-papel"
        aria-pressed={eligiendo === papel}
        onclick={() => (eligiendo = papel)}
      >
        <span class={`muestra muestra--${papel === 'origen' ? 'desde' : 'hasta'}`} aria-hidden="true"></span>
        {rotulo}
      </button>
      <p class="sendero__hueco-texto" class:sendero__hueco-texto--vacio={!nodo}>
        {nodo ? resumen(nodo.texto, 64) : copia.sinElegir}
      </p>
      {#if nodo}
        <button
          type="button"
          class="sendero__quitar"
          onclick={() => quitarExtremo(papel)}
          aria-label={`${copia.quitar} ${rotulo}`}
        >×</button>
      {/if}
    </div>
  {/snippet}

  <div class="sendero__mando">
    <!-- Los dos extremos, siempre a la vista: lo que hay puesto y cuál se está
         eligiendo. El buscador de abajo llena el que esté activo. -->
    <div class="sendero__extremos">
      {@render hueco('origen', copia.origen, origen)}
      {@render hueco('destino', copia.destino, destino)}
    </div>

    <div class="sendero__buscador">
      <label class="sendero__campo" for="sendero-busca"><span>{copia.busca}</span></label>
      <input
        id="sendero-busca"
        type="search"
        bind:value={filtro}
        disabled={cargando || fallo}
        placeholder={copia.buscaPista}
        aria-describedby="sendero-cuenta"
      />
      <p id="sendero-cuenta" class="sendero__cuenta-busca" aria-live="polite">
        {#if !aguja}{copia.conectados}
        {:else if coincidencias.length === 0}{copia.sinCoincidencias}
        {:else}{copia.coincidencias(coincidencias.length, resultados.length)}{/if}
      </p>
      <ul class="sendero__resultados">
        {#each resultados as nodo (nodo.id)}
          <li>
            <button
              type="button"
              class="sendero__resultado"
              data-elegido={nodo.id === origen ? 'origen' : nodo.id === destino ? 'destino' : null}
              onclick={() => ponerExtremo(nodo.id)}
              aria-label={`${copia.ponerComo(eligiendo === 'origen' ? copia.origen : copia.destino, resumen(nodo.texto, 76))} ${nodo.id === origen ? copia.origen : nodo.id === destino ? copia.destino : `${nodo.grado} ${copia.relaciones.toLocaleLowerCase(lang)}`} · ${rotuloSeccion(nodo.seccion, lang)}`}
            >
              <span class="sendero__punto" style={`background:${tintaDeSeccion(nodo.seccion)}`} aria-hidden="true"></span>
              <span class="sendero__resultado-texto">{resumen(nodo.texto, 76)}</span>
              {#if nodo.id === origen || nodo.id === destino}
                <span class="sendero__rol" data-papel={nodo.id === origen ? 'origen' : 'destino'}>
                  {nodo.id === origen ? copia.origen : copia.destino}
                </span>
              {:else}
                <span class="sendero__resultado-dato">{nodo.grado}</span>
              {/if}
            </button>
          </li>
        {/each}
      </ul>
    </div>

    <div class="sendero__botones">
      <button type="button" onclick={dosAlAzar} disabled={cargando || fallo}>{copia.azar}</button>
      <button type="button" onclick={limpiar} disabled={!origen && !destino && !abierta}>{copia.limpiar}</button>
    </div>
  </div>

  {#if !cargando && !fallo && grafo.nodos.length > 0}
    <p class="sendero__nota">
      {copia.nota(
        grafo.nodos.length,
        grafo.aristas.length,
        grafo.totales.citas,
        grafo.totales.traducciones,
        grafo.totales.aristas,
      )}
    </p>
  {/if}

  <div class="sendero__lectura" aria-live="polite">
    {#if fallo}
      <p role="alert" class="sendero__aviso">{copia.error}</p>
    {:else if cargando}
      <p class="sendero__aviso">{copia.cargando}</p>
    {:else if grafo.nodos.length === 0}
      <p class="sendero__aviso">{copia.vacio}</p>
    {:else if camino.length > 1}
      <h2>{copia.sendero} <span class="sendero__pasos">· {copia.pasos(camino.length - 1)}</span></h2>
      <ol class="sendero__lista">
        {#each camino as id, indice (id)}
          {@const nodo = porId.get(id)}
          {#if nodo}
            <li class:extremo={indice === 0 || indice === camino.length - 1}>
              <p class="sendero__cita" lang={nodo.idiomaTexto}>{nodo.texto}</p>
              <p class="sendero__meta">
                <button type="button" class="sendero__abrir" onclick={() => abrir(nodo.id)}>{nodo.idTexto}</button>
                · {rotuloSeccion(nodo.seccion, lang)}
                {#if nodo.idiomaTexto !== lang}· <em>{copia.sinTraducir}</em>{/if}
              </p>
            </li>
          {/if}
        {/each}
      </ol>
    {:else}
      <!-- Los más conectados ya no se repiten aquí: son lo que el buscador
           enseña de entrada, arriba, donde se eligen los extremos. -->
      <p class="sendero__aviso">{origen && destino ? copia.sinCamino : origen ? copia.soloUno : copia.pideDos}</p>
    {/if}
  </div>
</section>

<style>
  /* Tinta de noche: la misma materia del hero (tinta, seda, sello) en negativo.
     El valor baja de verdad — el fondo es tinta, no un beige aclarado — que es
     lo que daba planas las vistas claras. */
  /* El proyecto no trae reset: sin esto, un bloque con `inset` y `padding` se
     sale por los dos lados (la ficha y la línea de respuesta lo hacían). */
  .sendero :global(*) { box-sizing: border-box; }

  .sendero {
    --sendero-tinta: #12100b;
    --sendero-papel: #ece4d0;
    --sendero-apagado: #9d937e;
    /* Las dos regiones de la escena cuando hay una ficha abierta: el grafo
       arriba y la hoja abajo (a 390), o el grafo y la columna (en ancho). */
    --sendero-hoja: 58%;
    --sendero-columna: clamp(21.25rem, 28vw, 26.25rem);
    --sendero-curva: cubic-bezier(.2,.7,.2,1);
    background: radial-gradient(120% 90% at 50% 15%, #1d1a12 0%, #12100b 62%, #0c0a07 100%);
    color: var(--sendero-papel);
    padding-bottom: var(--ttod-space-12);
  }

  /* En móvil la constelación ocupa la pantalla entera: es el instrumento, no una
     ilustración de cabecera. El rótulo y la respuesta se montan encima, cada uno
     con su velo para que el texto no caiga sobre los puntos. */
  /* 61 px es lo que mide la barra de navegación pegajosa de `Page.astro`, que va
     en el flujo encima de esta sección: sin restarla, la escena se salía por
     abajo y la leyenda quedaba cortada (medido a 390, 768 y 1440). */
  .sendero__escena {
    --sendero-nav: 61px;
    position: relative;
    height: calc(100svh - var(--sendero-nav));
    min-height: 520px;
    overflow: hidden;
  }
  /* Con la ficha abierta la escena se recoge al hueco que queda libre: así la
     cámara centra el nodo tocado en lo que de verdad se ve, no debajo de la hoja. */
  .sendero__lienzo {
    position: absolute;
    inset: 0;
    /* El dedo que sube y baja es de la página: así nadie se queda atrapado en
       el grafo al intentar seguir leyendo. De lado, gira la escena. */
    touch-action: pan-y;
    /* El hueco se hace de golpe, no con una transición: `inset` es una medida
       del layout y animarla obliga a redimensionar el lienzo WebGL en cada
       fotograma (regla: por fotograma solo `transform` y
       `opacity`). Lo que se ve moverse es la cámara —320 ms— y la hoja
       llegando encima; el salto del encuadre queda tapado por el vuelo. */
  }
  /* Solo a 390: la hoja tapa media pantalla y la cámara tiene que centrar el
     nodo en lo que queda. En ancho la carta flota a un lado y el nodo cae en
     el centro, libre: el lienzo no cambia de tamaño (ni un `setSize`). */
  @media (max-width: 47.99rem) {
    .sendero__lienzo--ficha,
    .sendero__velo--ficha,
    .sendero__plano--ficha { bottom: var(--sendero-hoja); }
  }
  .sendero__lienzo--dormido { visibility: hidden; }
  /* El velo se encoge con el lienzo: si no, su banda oscura de abajo se queda
     detrás del papel y la línea de respuesta pierde el fondo que la hace
     legible (el contraste se mide sobre el píxel, no sobre el CSS). */
  /* El respaldo quieto ocupa el mismo hueco que el lienzo 3D y se encoge igual
     cuando se abre la ficha, para que la constelación no quede debajo. */
  .sendero__plano {
    position: absolute;
    inset: 0;
    touch-action: pan-y;
    cursor: pointer;
  }
  .sendero__plano canvas { display: block; }

  .sendero__velo {
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      linear-gradient(to bottom, rgba(12,10,7,.92) 0, rgba(12,10,7,.78) 24%, rgba(12,10,7,.35) 36%, rgba(12,10,7,0) 46%),
      linear-gradient(to top, rgba(12,10,7,.94) 0, rgba(12,10,7,.6) 16%, rgba(12,10,7,0) 34%);
  }

  .sendero__rotulo {
    position: absolute;
    inset-inline: 0;
    top: 0;
    padding: var(--ttod-space-8) clamp(1rem, 5vw, 2.5rem) var(--ttod-space-4);
    pointer-events: none;
    transition: opacity .3s ease;
  }
  /* Con la ficha abierta en móvil el titular se aparta: el trozo de escena que
     queda libre es estrecho y la cámara pone ahí el nodo tocado. */
  .sendero__rotulo--oculto { opacity: 0; }
  .sendero__rotulo h1 {
    font-family: var(--ttod-font-titular);
    font-weight: 300;
    font-size: clamp(2rem, 7vw, 3.6rem);
    line-height: 1.02;
    margin: 0;
    max-width: 16ch;
    color: var(--sendero-papel);
    text-wrap: balance;
  }
  .sendero__pista {
    font-family: var(--ttod-font-ui);
    /* 15 px, no los 13 del rótulo: es la instrucción de uso de la escena y a 390
       un texto de 13 px no se lee de un vistazo (revisar-pagina lo marcaba). */
    font-size: .9375rem;
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    margin: var(--ttod-space-3) 0 0;
    color: var(--sendero-apagado);
  }

  /* La línea de respuesta, como en la referencia: cuántos pasos tiene el sendero
     y de cuántos nodos y relaciones está hecho el mapa. */
  .sendero__respuesta {
    position: absolute;
    inset-inline: 0;
    bottom: 0;
    padding: var(--ttod-space-4) clamp(1rem, 5vw, 2.5rem) var(--ttod-space-6);
    display: grid;
    gap: var(--ttod-space-3);
  }
  /* Con la hoja abierta a 390, la línea de respuesta se sube al trozo de escena
     que queda libre en vez de quedarse debajo del papel; la leyenda se calla
     mientras la ficha explica el nodo, y vuelve al cerrarla. */
  @media (max-width: 47.99rem) {
    .sendero__respuesta--ficha { bottom: var(--sendero-hoja); padding-bottom: var(--ttod-space-3); }
    .sendero__respuesta--ficha .sendero__leyenda { display: none; }
  }
  .sendero__cifra {
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    margin: 0;
    color: #e5dcc4;
  }
  .sendero__cifra strong { color: #f0b64a; font-weight: 500; }
  /* A 390 la línea de respuesta tiene que caber en una sola: las versales con el
     tracking abierto se iban a dos y empujaban la leyenda fuera de pantalla. */
  @media (max-width: 30rem) { .sendero__cifra { letter-spacing: .015em; font-size: .78rem; } }
  .sendero__sep { color: var(--sendero-apagado); margin-inline: .25rem; }

  .sendero__leyenda {
    display: flex;
    flex-wrap: wrap;
    gap: var(--ttod-space-2) var(--ttod-space-6);
    list-style: none;
    margin: 0;
    padding: 0;
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    /* La leyenda se lee en caja baja: por encima de 0,05em se desarma la palabra. */
    letter-spacing: .01em;
    color: #cdc2a6;
  }
  .sendero__leyenda li { display: flex; align-items: center; gap: var(--ttod-space-2); }
  .muestra { width: .85rem; height: .85rem; border-radius: 50%; display: inline-block; }
  .muestra--desde { background: #6fd39b; box-shadow: 0 0 0 4px rgba(111,211,155,.2); }
  .muestra--hasta { background: #ff7a5c; box-shadow: 0 0 0 4px rgba(255,122,92,.2); }
  .muestra--paso { background: #f6ecd4; }
  .muestra--resto { background: linear-gradient(90deg, #c9a227, #6f8f7a 50%, #8d93b8); }
  .muestra--hilo { width: 1.6rem; height: 3px; border-radius: 2px; background: #f0b64a; }
  /* En móvil la leyenda se queda en los cuatro papeles que hay que distinguir
     para leer un sendero; el color por sección se explica solo al tocar un nodo. */
  @media (max-width: 30rem) { .sendero__leyenda li:last-child { display: none; } }

  /* El rótulo flotante de la librería viene con tipografía de sistema: se viste
     con la nuestra, que si no canta a plantilla. */
  .sendero :global(.graph-tooltip) {
    font-family: var(--ttod-font-body) !important;
    font-size: var(--ttod-text-base) !important;
    line-height: 1.4;
    max-width: 24ch;
    padding: .5rem .75rem;
    color: #f3ead4;
    background: rgba(16,14,9,.94);
    border: 1px solid #5d5445;
    border-radius: var(--ttod-radius-sm);
  }

  .sendero__giro {
    position: absolute;
    top: var(--ttod-space-8);
    inset-inline-end: clamp(1rem, 5vw, 2.5rem);
    min-height: 44px;
    padding: 0 var(--ttod-space-4);
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    color: #e5dcc4;
    background: rgba(18,16,11,.72);
    border: 1px solid #5d5445;
    border-radius: 999px;
    cursor: pointer;
  }
  .sendero__giro[aria-pressed='true'] { color: #12100b; background: #e5dcc4; border-color: #e5dcc4; }


  /* La carta. Una página arrancada del volumen de su sección: el mismo papel,
     la misma raya roja de margen y el mismo canto de hojas que la lectura de
     Sabiduría (`armario.css`, `.lectura-hoja`), para que el grafo y la
     biblioteca se sientan del mismo libro. El lomo lleva la tinta del nodo
     tocado: se sabe de qué estrella es la carta sin leer nada.
     A 390 es una hoja inferior que deja libre el trozo de escena donde la
     cámara pone el nodo; en ancho, una carta suelta a la derecha. */
  .sendero__ficha {
    --carta-margen: .5rem;
    position: absolute;
    inset-inline: var(--carta-margen);
    bottom: max(var(--carta-margen), env(safe-area-inset-bottom));
    height: calc(var(--sendero-hoja) - var(--carta-margen));
    display: flex;
    flex-direction: column;
    color: var(--ttod-color-ink);
    background:
      linear-gradient(260deg, rgb(27 23 16 / .10), transparent 7%),
      var(--ttod-color-surface-raised);
    border-left: 8px solid var(--lomo, #8a8270);
    border-radius: 4px 12px 12px 4px;
    /* Un solo canto de hojas, nítido: dos capas claras sobre la noche se
       leían como un borrón en la esquina. */
    box-shadow:
      4px 3px 0 -1px #d8ccb1,
      0 28px 56px -24px rgb(0 0 0 / .85);
    overflow: hidden;
    /* Capa propia: arrastrarla y su entrada mueven una textura ya pintada. */
    will-change: transform;
  }
  /* La raya roja del margen, la de las hojas de la estantería. */
  .sendero__ficha::before {
    content: "";
    position: absolute;
    inset-block: 0;
    left: 1.1rem;
    width: 1px;
    background: color-mix(in srgb, var(--ttod-color-seal) 42%, transparent);
    pointer-events: none;
  }
  /* El foco se pone a mano para que el lector de pantalla entre en la carta;
     no es una parada de tabulador, así que no se le pinta el cerco. */
  .sendero__ficha:focus { outline: none; }

  /* Cabecera fija: sello, volumen y folio, y la ×. Es el asa de la hoja. */
  .sendero__ficha-cabeza {
    position: relative;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: var(--ttod-space-3);
    padding: var(--ttod-space-4) var(--ttod-space-3) var(--ttod-space-2) 1.75rem;
    touch-action: none;
    cursor: grab;
  }
  .sendero__asa {
    position: absolute;
    top: .4rem;
    left: 50%;
    width: 2.25rem;
    height: 4px;
    margin-left: -1.125rem;
    border-radius: 2px;
    background: var(--ttod-color-line-subtle);
  }
  /* El sello: la inicial de la sección en rojo, como en la tapa de los libros. */
  .sendero__sello {
    display: grid;
    place-items: center;
    width: 2rem;
    height: 2rem;
    font: 500 1.05rem/1 var(--ttod-font-titular);
    color: #f6ece0;
    background: var(--ttod-color-seal);
    box-shadow: inset 0 0 0 1px rgb(0 0 0 / .3);
    transform: rotate(-3deg);
  }
  .sendero__ficha-volumen {
    display: grid;
    gap: .15rem;
    min-width: 0;
    margin: 0;
    font: 500 var(--ttod-text-ui) / 1.25 var(--ttod-font-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    color: var(--ttod-color-ink);
  }
  .sendero__ficha-folio { font-weight: 400; color: var(--ttod-color-muted); }
  /* La × es un botón redondo de 44 px sin caja: pertenece al papel. */
  .sendero__cerrar {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    padding: 0;
    color: var(--ttod-color-ink);
    background: transparent;
    border: 0;
    border-radius: 50%;
    cursor: pointer;
  }
  .sendero__cerrar:hover { background: rgb(33 28 21 / .07); }
  .sendero__cerrar:focus-visible { outline: 2px solid var(--ttod-color-ink); outline-offset: 2px; }

  .sendero__ficha-cuerpo {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: var(--ttod-space-2) var(--ttod-space-4) var(--ttod-space-6) 1.75rem;
    transition: opacity 120ms linear;
  }
  .sendero__ficha-cuerpo--cruza { opacity: 0; }
  .sendero__punto { width: .6rem; height: .6rem; border-radius: 50%; display: inline-block; flex: none; }
  /* El aforismo, con la voz de los titulares: lo único grande de la carta. */
  .sendero__ficha-cita {
    font-family: var(--ttod-font-titular);
    font-weight: 300;
    font-size: clamp(1.4rem, 5.6vw, 1.8rem);
    line-height: 1.22;
    margin: 0;
    padding: 0;
    color: var(--ttod-color-ink);
    text-wrap: pretty;
    hyphens: none;
  }
  /* Un aforismo de cinco frases no cabe en la voz grande sin echar los
     botones fuera de la carta: baja un escalón. */
  .sendero__ficha-cita--larga { font-size: clamp(1.2rem, 4.6vw, 1.45rem); line-height: 1.3; }
  .sendero__ficha-nota,
  .sendero__ficha-glosa {
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-base);
    line-height: 1.5;
    color: var(--ttod-color-muted);
    margin: var(--ttod-space-4) 0 0;
  }
  .sendero__ficha-glosa { font-style: italic; }
  .sendero__ficha-nota { font-size: var(--ttod-text-sm); font-style: italic; }
  /* Las dos marcas, a medias y donde llega el pulgar; debajo, la ficha entera. */
  .sendero__ficha-acciones {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--ttod-space-2);
    margin: var(--ttod-space-6) 0 0;
  }
  .sendero__marcar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--ttod-space-2);
    min-height: 44px;
    padding: 0 var(--ttod-space-3);
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    white-space: nowrap;
    color: var(--ttod-color-ink);
    background: transparent;
    border: 1px solid var(--ttod-color-line);
    border-radius: 999px;
    cursor: pointer;
  }
  .sendero__marcar .muestra { width: .6rem; height: .6rem; box-shadow: none; }
  .sendero__marcar[aria-pressed='true'] {
    color: var(--ttod-color-paper);
    background: var(--ttod-color-ink);
    border-color: var(--ttod-color-ink);
  }
  .sendero__ficha-enlace {
    grid-column: 1 / -1;
    display: inline-flex;
    align-items: center;
    gap: .35rem;
    min-height: 44px;
    font: 500 var(--ttod-text-sm) / 1.3 var(--ttod-font-ui);
    color: var(--ttod-color-accent);
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 4px;
  }
  .sendero__ficha-titulo {
    display: flex;
    align-items: baseline;
    gap: var(--ttod-space-3);
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    color: var(--ttod-color-muted);
    font-weight: 400;
    margin: var(--ttod-space-6) 0 var(--ttod-space-2);
  }
  .sendero__cuenta { font-family: var(--ttod-font-body); font-size: var(--ttod-text-base); letter-spacing: 0; color: var(--ttod-color-ink); }
  /* Los vecinos son filas de lista de ancho completo, no píldoras: el texto a
     la izquierda y su número de relaciones a la derecha (Are.na). */
  .sendero__vecinos { list-style: none; margin: 0; padding: 0; }
  .sendero__vecinos li { border-bottom: 1px solid var(--ttod-color-line-subtle); }
  .sendero__vecinos li:first-child { border-top: 1px solid var(--ttod-color-line-subtle); }
  .sendero__vecinos button {
    display: flex;
    align-items: center;
    gap: var(--ttod-space-3);
    width: 100%;
    min-height: 44px;
    padding: var(--ttod-space-3) 0;
    text-align: start;
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-base);
    line-height: 1.4;
    color: var(--ttod-color-ink);
    background: transparent;
    border: 0;
    cursor: pointer;
  }
  .sendero__vecino-texto { flex: 1; }
  .sendero__vecino-dato {
    flex: none;
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    /* Cifras de ancho fijo: la columna de la derecha es una columna, no una
       sucesión de números que bailan según el dígito. */
    font-variant-numeric: tabular-nums;
    color: var(--ttod-color-muted);
  }
  .sendero__vecinos button:hover .sendero__vecino-texto,
  .sendero__vecinos button:focus-visible .sendero__vecino-texto { text-decoration: underline; text-underline-offset: 3px; }
  .sendero__mando {
    display: grid;
    gap: var(--ttod-space-4);
    padding: var(--ttod-space-8) clamp(1rem, 5vw, 2.5rem) 0;
  }
  .sendero__campo { display: grid; gap: var(--ttod-space-2); }
  .sendero__campo span {
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    color: #cdc2a6;
  }
  .sendero__buscador input {
    min-height: 44px;
    width: 100%;
    padding: 0 var(--ttod-space-3);
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-base);
    color: var(--sendero-papel);
    background: #1b1710;
    border: 1px solid #5d5445;
    border-radius: var(--ttod-radius-sm);
  }
  .sendero__buscador input::placeholder { color: #8d836e; }

  /* Los dos extremos: dos huecos de papel sobre la tinta. El que está activo
     —el que llenará lo próximo que toques— se marca con el filo claro y el
     fondo encendido, no solo con color: a 390 y en gris hay que distinguirlo. */
  .sendero__extremos { display: grid; gap: var(--ttod-space-3); }
  .sendero__hueco {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    gap: var(--ttod-space-2) var(--ttod-space-3);
    padding: var(--ttod-space-3) var(--ttod-space-4);
    border: 1px solid #3a352a;
    border-radius: var(--ttod-radius-sm);
    background: rgba(255,255,255,.02);
  }
  .sendero__hueco--activo {
    border-color: #e7c478;
    background: rgba(231,196,120,.08);
  }
  .sendero__hueco-papel {
    display: flex;
    align-items: center;
    gap: var(--ttod-space-2);
    min-height: 44px;
    padding: 0;
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    color: #cdc2a6;
    background: none;
    border: 0;
    cursor: pointer;
  }
  .sendero__hueco--activo .sendero__hueco-papel { color: #f3ead4; }
  .sendero__hueco-texto {
    grid-column: 1 / -1;
    margin: 0;
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-base);
    line-height: 1.4;
    color: #ddd3bb;
  }
  /* Vacío, el hueco es un solo renglón: dos huecos sin elegir ocupaban 220 px
     de los 844 de la pantalla antes de llegar al buscador (medido en la captura
     de Safari a 390). Lleno, baja a su propio renglón y se lee entero. */
  .sendero__hueco-texto--vacio {
    grid-column: 2;
    grid-row: 1;
    text-align: end;
    color: var(--sendero-apagado);
    font-style: italic;
  }
  .sendero__quitar {
    grid-row: 1;
    grid-column: 2;
    width: 44px;
    height: 44px;
    font-size: 1.25rem;
    line-height: 1;
    color: #cdc2a6;
    background: none;
    border: 1px solid #3a352a;
    border-radius: var(--ttod-radius-sm);
    cursor: pointer;
  }
  .sendero__quitar:hover,
  .sendero__quitar:focus-visible { color: #f3ead4; border-color: #e7c478; }

  .sendero__buscador { display: grid; gap: var(--ttod-space-2); }
  /* En minúsculas y con la tipografía del texto: dos renglones seguidos en
     versalitas con interletraje (el rótulo del campo y esta cuenta) pesaban más
     que los propios aforismos. */
  .sendero__cuenta-busca {
    margin: 0;
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-base);
    color: var(--sendero-apagado);
  }
  .sendero__resultados { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--ttod-space-2); }
  .sendero__resultado {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: baseline;
    gap: var(--ttod-space-3);
    width: 100%;
    min-height: 44px;
    padding: var(--ttod-space-3) var(--ttod-space-4);
    text-align: start;
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-base);
    line-height: 1.4;
    color: #ddd3bb;
    background: rgba(255,255,255,.03);
    border: 1px solid #3a352a;
    border-radius: var(--ttod-radius-sm);
    cursor: pointer;
  }
  .sendero__resultado:hover,
  .sendero__resultado:focus-visible { border-color: #e7c478; color: #f3ead4; }
  /* El que ya es un extremo se queda marcado con su tinta aunque pierda el
     foco: la fila dice su papel y el filo lo repite sin leer. */
  .sendero__resultado[data-elegido='origen'] { border-color: #6fd39b; background: rgba(111,211,155,.07); }
  .sendero__resultado[data-elegido='destino'] { border-color: #ff7a5c; background: rgba(255,122,92,.07); }
  .sendero__resultado .sendero__punto { transform: translateY(-1px); }
  /* El número de relaciones va sobre tinta, no sobre papel: con el gris apagado
     del sitio claro (`--ttod-color-muted`) se quedaba en 2,07:1 sobre la ficha
     oscura —medido en las tres anchuras—. Con la tinta apagada
     de la nota (#b7ab92, la que ya pasa el contraste en esta misma vista) sube a
     8:1 de cálculo, que a 13 px deja margen para lo que pierde el suavizado. */
  .sendero__resultado-dato {
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    font-variant-numeric: tabular-nums;
    color: #b7ab92;
  }
  .sendero__rol {
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    white-space: nowrap;
  }
  .sendero__rol[data-papel='origen'] { color: #6fd39b; }
  .sendero__rol[data-papel='destino'] { color: #ff7a5c; }
  .sendero__botones { display: flex; gap: var(--ttod-space-3); flex-wrap: wrap; }
  .sendero__botones button {
    min-height: 44px;
    padding: 0 var(--ttod-space-6);
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: var(--ttod-tracking-ui);
    text-transform: uppercase;
    color: #12100b;
    background: var(--sendero-papel);
    border: 1px solid var(--sendero-papel);
    border-radius: 999px;
    cursor: pointer;
  }
  .sendero__botones button:last-child {
    color: var(--sendero-papel);
    background: transparent;
    border-color: #5d5445;
  }
  /*
   * Mientras llegan los aforismos, los dos botones esperan. Esperar no es
   * desaparecer: bajarles la opacidad al 45 % dejaba la tinta del relleno en
   * 3,7:1 sobre el fondo (medido sobre la captura a 768 y a 1440, mínimo 4,5:1),
   * o sea un rótulo que no se lee. Esperando son el mismo botón vaciado —sin
   * relleno, con el filo apagado— y el rótulo sigue en 8:1.
   */
  .sendero__botones button[disabled],
  .sendero__botones button[disabled]:last-child {
    cursor: default;
    color: #b7ab92;
    background: transparent;
    border-color: #4a4337;
  }

  .sendero__nota {
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-base);
    line-height: 1.5;
    max-width: 58ch;
    margin: var(--ttod-space-6) 0 0;
    padding-inline: clamp(1rem, 5vw, 2.5rem);
    color: #b7ab92;
  }

  .sendero__lectura {
    padding: var(--ttod-space-8) clamp(1rem, 5vw, 2.5rem) 0;
    max-width: 62rem;
  }
  .sendero__lectura h2 {
    font-family: var(--ttod-font-titular);
    font-weight: 300;
    font-size: clamp(1.5rem, 4.5vw, 2.2rem);
    margin: 0 0 var(--ttod-space-6);
  }
  .sendero__pasos { color: #f0b64a; }
  .sendero__aviso {
    font-family: var(--ttod-font-body);
    font-size: var(--ttod-text-lg);
    line-height: 1.55;
    max-width: 46ch;
    margin: 0;
    color: #ddd3bb;
  }
  .sendero__lista { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--ttod-space-6); }
  .sendero__lista li {
    border-inline-start: 2px solid #4a4335;
    padding-inline-start: var(--ttod-space-4);
  }
  .sendero__lista li.extremo { border-inline-start-color: #f0b64a; }
  .sendero__cita {
    font-family: var(--ttod-font-body);
    font-size: clamp(1.0625rem, 3.6vw, 1.35rem);
    line-height: 1.5;
    margin: 0;
    color: var(--sendero-papel);
  }
  .sendero__meta {
    font-family: var(--ttod-font-ui);
    font-size: var(--ttod-text-ui);
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #b7ab92;
    margin: var(--ttod-space-2) 0 0;
  }
  /* Lo que se toca se toca con el dedo: 44 px de alto, no una línea de 16. */
  .sendero__abrir {
    color: #e7c478;
    display: inline-flex;
    align-items: center;
    min-height: 44px;
    padding-inline: var(--ttod-space-3);
    margin-inline-start: calc(var(--ttod-space-3) * -1);
    border: 0;
    border-radius: 999px;
    background: transparent;
    font: inherit;
    letter-spacing: inherit;
    text-transform: inherit;
    cursor: pointer;
  }
  .sendero__abrir:hover,
  .sendero__abrir:focus-visible { background: rgba(231, 196, 120, .14); }

  @media (min-width: 48rem) {
    /* En ancho: a la izquierda los dos extremos y los botones, a la derecha el
       buscador con sus resultados, que es la columna que cambia al escribir. */
    .sendero__mando {
      grid-template-columns: minmax(18rem, 24rem) 1fr;
      align-items: start;
      column-gap: var(--ttod-space-8);
    }
    .sendero__buscador { grid-column: 2; grid-row: 1 / span 2; }
    .sendero__escena { height: 92svh; }
    .sendero__rotulo { top: clamp(3rem, 5vw, 5rem); max-width: 40ch; }
    .sendero__rotulo--oculto { opacity: 1; }
    /* En ancho la carta es una pieza suelta a la derecha, alta lo que pide su
       texto y no la pantalla entera: bajo el botón de girar, separada de los
       bordes, con la constelación respirando alrededor. */
    .sendero__ficha {
      --carta-margen: clamp(1rem, 2.5vw, 2.5rem);
      inset-inline: auto var(--carta-margen);
      top: calc(var(--ttod-space-8) + 44px + var(--ttod-space-4));
      bottom: auto;
      width: var(--sendero-columna);
      height: auto;
      max-height: calc(100% - var(--ttod-space-8) - 44px - var(--ttod-space-4) - var(--carta-margen));
    }
    .sendero__asa { display: none; }
    .sendero__ficha-cabeza { cursor: auto; padding-top: var(--ttod-space-4); touch-action: auto; }
    /* La línea de respuesta se queda a la izquierda de la carta y, en vez de
       apretarse en una fila, apila la cifra sobre la leyenda. */
    .sendero__respuesta.sendero__respuesta--ficha {
      inset-inline-end: calc(var(--sendero-columna) + 2 * clamp(1rem, 2.5vw, 2.5rem));
      flex-direction: column;
      align-items: flex-start;
      gap: var(--ttod-space-3);
    }
    .sendero__respuesta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: var(--ttod-space-8);
    }
  }

  /* Un solo escalón, no una cascada: la hoja llega y 40 ms después el aforismo.
     El resto del contenido entra con la hoja. */
  @media (prefers-reduced-motion: no-preference) {
    .sendero__ficha-cita { animation: aforismo-entra 240ms var(--sendero-curva) 120ms both; }
  }
  @keyframes aforismo-entra {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: none; }
  }

  @media (prefers-reduced-motion: reduce) {
    .sendero__lienzo { cursor: default; }
    .sendero__ficha-cuerpo { transition: none; }
  }
</style>

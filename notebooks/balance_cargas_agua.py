#!/usr/bin/env python3
# =============================================================================
#  BALANCE DE CARGAS EN ANÁLISIS QUÍMICO DE AGUAS
#  Autor: Herramienta Hidrogeoquímica Interactiva
#  Versión: 2.0 - Nivel Ingeniería
# =============================================================================
#
#  TEORÍA:
#  El balance de cargas se basa en la electroneutralidad del agua:
#    Σ cationes (meq/L) = Σ aniones (meq/L)
#
#  Conversión:
#    meq/L = (mg/L / Peso Molecular) × Valencia
#
#  Error de Balance de Cargas (CBE):
#    CBE (%) = [(ΣC - ΣA) / (ΣC + ΣA)] × 100
#
#  Criterio de aceptación:
#    |CBE| < 5%  → análisis aceptable
#    |CBE| ≥ 5%  → repetir análisis
# =============================================================================

import csv
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.columns import Columns
from rich.rule import Rule
from rich.align import Align
import time

# ─── Consola principal con estilo ────────────────────────────────────────────
console = Console()

# =============================================================================
#  CONSTANTES FISICOQUÍMICAS
#  Peso Molecular (g/mol) y Valencia de cada ion
# =============================================================================

CATIONES = {
    "Na⁺"  : {"formula": "Na+",   "pm": 22.990, "valencia": 1, "nombre": "Sodio"},
    "K⁺"   : {"formula": "K+",    "pm": 39.098, "valencia": 1, "nombre": "Potasio"},
    "Ca²⁺" : {"formula": "Ca2+",  "pm": 40.078, "valencia": 2, "nombre": "Calcio"},
    "Mg²⁺" : {"formula": "Mg2+",  "pm": 24.305, "valencia": 2, "nombre": "Magnesio"},
    "Li⁺"  : {"formula": "Li+",   "pm": 6.941,  "valencia": 1, "nombre": "Litio"},
}

ANIONES = {
    "Cl⁻"   : {"formula": "Cl-",   "pm": 35.453, "valencia": 1, "nombre": "Cloruro"},
    "F⁻"    : {"formula": "F-",    "pm": 18.998, "valencia": 1, "nombre": "Fluoruro"},
    "SO₄²⁻" : {"formula": "SO42-", "pm": 96.060, "valencia": 2, "nombre": "Sulfato"},
    "PO₄³⁻" : {"formula": "PO43-", "pm": 94.971, "valencia": 3, "nombre": "Fosfato"},
    "HCO₃⁻" : {"formula": "HCO3-", "pm": 61.016, "valencia": 1, "nombre": "Bicarbonato"},
    "CO₃²⁻" : {"formula": "CO32-", "pm": 60.008, "valencia": 2, "nombre": "Carbonato"},
}

# Colores para la UI
COLOR_TITULO    = "bold cyan"
COLOR_OK        = "bold green"
COLOR_ERROR     = "bold red"
COLOR_ADVERTENCIA = "bold yellow"
COLOR_INFO      = "bold white"
COLOR_SECUNDARIO = "dim white"
COLOR_RESALTADO = "bold magenta"


# =============================================================================
#  FUNCIONES PRINCIPALES
# =============================================================================

def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_bienvenida():
    """Muestra el banner principal de bienvenida."""
    limpiar_pantalla()
    console.print()
    
    banner = Text()
    banner.append("  ══════════════════════════════════════════════════════════\n", style="cyan")
    banner.append("  ██████  ██   ██  ██████  ██████  ██████  ██████  ██████ \n", style="bold cyan")
    banner.append("    ██    ██   ██    ██    ██      ██  ██  ██  ██  ██  ██ \n", style="bold cyan")
    banner.append("    ██    ███████    ██    ███████ ██████  ██████  ██  ██ \n", style="bold cyan")
    banner.append("    ██    ██   ██    ██    ██   ██ ██  ██  ██  ██  ██  ██ \n", style="bold cyan")
    banner.append("    ██    ██   ██  ██████  ██████  ██  ██  ██  ██  ██████ \n", style="bold cyan")
    banner.append("  ══════════════════════════════════════════════════════════\n", style="cyan")
    
    console.print(banner)
    
    console.print(Panel.fit(
        "[bold white]⚗️  Herramienta de Balance de Cargas Iónicas en Aguas[/bold white]\n"
        "[dim]Análisis Hidrogeoquímico • Criterio de Electroneutralidad[/dim]\n"
        "[dim cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim cyan]\n"
        "[italic dim]  Cationes: Na⁺  K⁺  Ca²⁺  Mg²⁺  Li⁺[/italic dim]\n"
        "[italic dim]  Aniones:  Cl⁻  F⁻  SO₄²⁻  PO₄³⁻  HCO₃⁻  CO₃²⁻[/italic dim]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print()


def mostrar_teoria():
    """Explica brevemente la teoría del balance de cargas."""
    console.print(Panel(
        "[bold white]📚 FUNDAMENTO TEÓRICO[/bold white]\n\n"
        "[cyan]Principio de Electroneutralidad:[/cyan]\n"
        "  En toda solución acuosa en equilibrio, la suma de cargas\n"
        "  positivas (cationes) DEBE ser igual a la suma de cargas\n"
        "  negativas (aniones).\n\n"
        "[cyan]Conversión:[/cyan]\n"
        "  [bold]meq/L = (mg/L ÷ Peso Molecular) × Valencia[/bold]\n\n"
        "[cyan]Error de Balance de Cargas (CBE):[/cyan]\n"
        "  [bold]CBE(%) = [(ΣC − ΣA) / (ΣC + ΣA)] × 100[/bold]\n\n"
        "[cyan]Criterio de aceptación (Appelo & Postma, 2005):[/cyan]\n"
        "  [green]✓  |CBE| < 5%[/green]  →  Análisis [bold green]ACEPTABLE[/bold green]\n"
        "  [red]✗  |CBE| ≥ 5%[/red]  →  Análisis [bold red]RECHAZADO[/bold red] — repetir",
        border_style="blue",
        padding=(1, 3),
    ))
    console.print()


def mg_a_meq(concentracion_mg_L: float, peso_molecular: float, valencia: int) -> float:
    """
    Convierte concentración de mg/L a meq/L.

    Parámetros
    ----------
    concentracion_mg_L : float
        Concentración del ion en miligramos por litro.
    peso_molecular : float
        Peso molecular del ion en g/mol.
    valencia : int
        Valencia (carga iónica) del ion.

    Retorna
    -------
    float
        Concentración en miliequivalentes por litro (meq/L).
    """
    if peso_molecular <= 0:
        raise ValueError("El peso molecular debe ser mayor que cero.")
    return (concentracion_mg_L / peso_molecular) * valencia


def calcular_balance(cationes_meq: dict, aniones_meq: dict) -> dict:
    """
    Calcula el balance de cargas iónicas.

    Parámetros
    ----------
    cationes_meq : dict  {nombre_ion: meq/L}
    aniones_meq  : dict  {nombre_ion: meq/L}

    Retorna
    -------
    dict con:
        suma_cationes, suma_aniones, cbe (%), evaluacion, diferencia
    """
    suma_cationes = sum(cationes_meq.values())
    suma_aniones  = sum(aniones_meq.values())
    diferencia    = suma_cationes - suma_aniones
    denominador   = suma_cationes + suma_aniones

    if denominador == 0:
        cbe = 0.0
    else:
        cbe = (diferencia / denominador) * 100.0

    if abs(cbe) < 5.0:
        evaluacion = "ACEPTABLE"
    else:
        evaluacion = "RECHAZADO"

    return {
        "suma_cationes": suma_cationes,
        "suma_aniones" : suma_aniones,
        "diferencia"   : diferencia,
        "cbe"          : cbe,
        "evaluacion"   : evaluacion,
    }


def ingresar_ion(nombre: str, formula: str, pm: float, valencia: int,
                 tipo: str, indice: int, total: int) -> float:
    """
    Solicita al usuario la concentración de un ion de forma interactiva y guiada.

    Parámetros
    ----------
    nombre   : str   Nombre del ion (ej. 'Sodio')
    formula  : str   Fórmula química (ej. 'Na+')
    pm       : float Peso molecular
    valencia : int   Valencia
    tipo     : str   'Catión' o 'Anión'
    indice   : int   Posición en la lista (para mostrar progreso)
    total    : int   Total de iones a ingresar

    Retorna
    -------
    float : Concentración en mg/L (0.0 si no está presente)
    """
    color = "cyan" if tipo == "Catión" else "magenta"
    
    console.print(
        f"  [{color}][{indice}/{total}][/{color}] "
        f"[bold white]{nombre}[/bold white] "
        f"[dim]({formula})[/dim]  "
        f"[dim]PM={pm:.3f} g/mol | z={valencia}[/dim]"
    )
    
    while True:
        try:
            entrada = Prompt.ask(
                f"       [dim]Concentración en mg/L[/dim] "
                f"[dim](Enter = 0 si no está presente)[/dim]",
                default="0",
                console=console
            )
            valor = float(entrada.replace(",", "."))
            if valor < 0:
                console.print("  [yellow]⚠  El valor no puede ser negativo. Ingrese 0 si no detectado.[/yellow]")
                continue
            return valor
        except ValueError:
            console.print("  [red]✗  Por favor ingrese un número válido (ej: 125.5)[/red]")


def mostrar_tabla_conversion(datos_iones: list, tipo: str) -> dict:
    """
    Muestra una tabla de conversión mg/L → meq/L y retorna los meq/L calculados.

    Parámetros
    ----------
    datos_iones : list de dict con keys: simbolo, nombre, pm, valencia, mg_L
    tipo        : str  'Cationes' o 'Aniones'

    Retorna
    -------
    dict {simbolo: meq/L}
    """
    color_encabezado = "cyan" if tipo == "Cationes" else "magenta"
    emoji = "⊕" if tipo == "Cationes" else "⊖"
    
    tabla = Table(
        title=f"[bold {color_encabezado}]{emoji} {tipo.upper()}[/bold {color_encabezado}]",
        box=box.ROUNDED,
        border_style=color_encabezado,
        show_header=True,
        header_style=f"bold {color_encabezado}",
        padding=(0, 1),
    )
    
    tabla.add_column("Símbolo",      style="bold white",  justify="center", min_width=9)
    tabla.add_column("Nombre",       style="white",       justify="left",   min_width=12)
    tabla.add_column("mg/L",         style="yellow",      justify="right",  min_width=9)
    tabla.add_column("P.M. (g/mol)", style="dim white",   justify="right",  min_width=12)
    tabla.add_column("Valencia",     style="dim white",   justify="center", min_width=8)
    tabla.add_column("meq/L",        style=f"bold {color_encabezado}", justify="right", min_width=9)
    tabla.add_column("Fórmula",      style="italic dim",  justify="left",   min_width=22)
    
    resultados = {}
    
    for ion in datos_iones:
        meq = mg_a_meq(ion["mg_L"], ion["pm"], ion["valencia"])
        resultados[ion["simbolo"]] = meq
        
        # Solo mostrar iones con concentración > 0
        if ion["mg_L"] > 0:
            formula_calc = (
                f"({ion['mg_L']:.3f} / {ion['pm']:.3f}) × {ion['valencia']}"
                f" = {meq:.4f}"
            )
            tabla.add_row(
                ion["simbolo"],
                ion["nombre"],
                f"{ion['mg_L']:.3f}",
                f"{ion['pm']:.3f}",
                str(ion["valencia"]),
                f"{meq:.4f}",
                formula_calc,
            )
        else:
            tabla.add_row(
                ion["simbolo"],
                ion["nombre"],
                "[dim]0.000[/dim]",
                f"{ion['pm']:.3f}",
                str(ion["valencia"]),
                "[dim]0.0000[/dim]",
                "[dim]no detectado[/dim]",
                style="dim",
            )
    
    console.print(tabla)
    return resultados


def mostrar_resultado_balance(resultado: dict, id_muestra: str):
    """
    Muestra el resultado final del balance de cargas con formato visual detallado.

    Parámetros
    ----------
    resultado   : dict  Salida de calcular_balance()
    id_muestra  : str   Identificador de la muestra
    """
    cbe     = resultado["cbe"]
    eval_   = resultado["evaluacion"]
    suma_c  = resultado["suma_cationes"]
    suma_a  = resultado["suma_aniones"]
    dif     = resultado["diferencia"]
    
    # Barra de progreso visual del CBE
    abs_cbe = abs(cbe)
    barra_llena   = min(int(abs_cbe * 2), 40)  # escala: 0-20% → 0-40 chars
    barra_vacia   = 40 - barra_llena
    color_barra   = "green" if abs_cbe < 5 else "red" if abs_cbe > 10 else "yellow"
    barra = f"[{color_barra}]{'█' * barra_llena}[/{color_barra}][dim]{'░' * barra_vacia}[/dim]"
    
    if eval_ == "ACEPTABLE":
        icono_eval  = "✅"
        color_eval  = "bold green"
        mensaje     = "El análisis cumple con el criterio de electroneutralidad."
        accion      = "✓  Los datos pueden usarse con confianza para modelado geoquímico."
    else:
        icono_eval  = "❌"
        color_eval  = "bold red"
        mensaje     = "El análisis NO cumple con el criterio de electroneutralidad."
        accion      = (
            "✗  Posibles causas: iones no medidos, errores en dilución,\n"
            "   contaminación de muestras o errores de laboratorio.\n"
            "   → Se recomienda [bold]repetir el análisis.[/bold]"
        )
    
    console.print()
    console.print(Rule(f"[bold white]📊 RESULTADOS — Muestra: {id_muestra}[/bold white]", style="white"))
    console.print()
    
    # Tabla de sumas
    tabla_res = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    tabla_res.add_column(style="bold white",   min_width=30)
    tabla_res.add_column(style="bold yellow",  min_width=14, justify="right")
    tabla_res.add_column(style="dim white",    min_width=8)
    
    tabla_res.add_row("⊕  Suma de Cationes (ΣC)",   f"{suma_c:.4f}", "meq/L")
    tabla_res.add_row("⊖  Suma de Aniones  (ΣA)",   f"{suma_a:.4f}", "meq/L")
    tabla_res.add_row("   Diferencia  (ΣC − ΣA)",   f"{dif:+.4f}",  "meq/L")
    tabla_res.add_section()
    tabla_res.add_row(
        "📐 CBE = (ΣC−ΣA)/(ΣC+ΣA) × 100",
        f"[bold {'green' if abs_cbe < 5 else 'red'}]{cbe:+.2f}[/bold {'green' if abs_cbe < 5 else 'red'}]",
        "%"
    )
    
    console.print(tabla_res)
    console.print()
    
    # Barra visual
    console.print(f"  [dim]CBE:[/dim] {barra}  [{color_barra}]{cbe:+.2f}%[/{color_barra}]")
    console.print(f"  [dim]     0%{'':>8}5%{'':>11}10%{'':>9}15%{'':>7}20%[/dim]")
    console.print()
    
    # Veredicto final
    console.print(Panel(
        f"[{color_eval}]{icono_eval}  {eval_}[/{color_eval}]\n\n"
        f"[white]{mensaje}[/white]\n\n"
        f"[dim]{accion}[/dim]",
        title=f"[bold white]EVALUACIÓN — {id_muestra}[/bold white]",
        border_style="green" if eval_ == "ACEPTABLE" else "red",
        padding=(1, 3),
    ))
    console.print()


def capturar_muestra_interactiva() -> tuple[str, dict, dict]:
    """
    Guía al usuario paso a paso para ingresar todos los datos de una muestra.

    Retorna
    -------
    tuple (id_muestra, cationes_mg, aniones_mg)
        Donde cationes_mg y aniones_mg son dicts {simbolo: mg/L}
    """
    console.print()
    console.print(Rule("[bold cyan]🧪 NUEVA MUESTRA[/bold cyan]", style="cyan"))
    console.print()
    
    id_muestra = Prompt.ask(
        "  [bold white]Ingrese el ID de la muestra[/bold white] "
        "[dim](ej: SF11, Pozo-01, ManantialA)[/dim]",
        default="MUESTRA_01",
        console=console
    )
    
    console.print()
    console.print(Panel(
        "[bold cyan]⊕  INGRESO DE CATIONES[/bold cyan]\n"
        "[dim]Ingrese la concentración en mg/L de cada catión.\n"
        "Si el ion no fue detectado o no se analizó, presione Enter (valor = 0).[/dim]",
        border_style="cyan", padding=(0, 2)
    ))
    console.print()
    
    cationes_datos = []
    total_cat = len(CATIONES)
    for i, (simbolo, info) in enumerate(CATIONES.items(), start=1):
        mg_L = ingresar_ion(
            nombre   = info["nombre"],
            formula  = info["formula"],
            pm       = info["pm"],
            valencia = info["valencia"],
            tipo     = "Catión",
            indice   = i,
            total    = total_cat
        )
        cationes_datos.append({
            "simbolo" : simbolo,
            "nombre"  : info["nombre"],
            "pm"      : info["pm"],
            "valencia": info["valencia"],
            "mg_L"    : mg_L,
        })
        console.print()
    
    console.print()
    console.print(Panel(
        "[bold magenta]⊖  INGRESO DE ANIONES[/bold magenta]\n"
        "[dim]Ingrese la concentración en mg/L de cada anión.[/dim]",
        border_style="magenta", padding=(0, 2)
    ))
    console.print()
    
    aniones_datos = []
    total_ani = len(ANIONES)
    for i, (simbolo, info) in enumerate(ANIONES.items(), start=1):
        mg_L = ingresar_ion(
            nombre   = info["nombre"],
            formula  = info["formula"],
            pm       = info["pm"],
            valencia = info["valencia"],
            tipo     = "Anión",
            indice   = i,
            total    = total_ani
        )
        aniones_datos.append({
            "simbolo" : simbolo,
            "nombre"  : info["nombre"],
            "pm"      : info["pm"],
            "valencia": info["valencia"],
            "mg_L"    : mg_L,
        })
        console.print()
    
    return id_muestra, cationes_datos, aniones_datos


def procesar_y_mostrar_muestra(id_muestra: str, cationes_datos: list, aniones_datos: list) -> dict:
    """
    Ejecuta la conversión, muestra tablas y calcula el balance de una muestra.

    Parámetros
    ----------
    id_muestra     : str
    cationes_datos : list de dicts con datos de cationes (incluye mg_L)
    aniones_datos  : list de dicts con datos de aniones  (incluye mg_L)

    Retorna
    -------
    dict con todos los resultados para el resumen final.
    """
    console.print()
    console.print(Rule(
        f"[bold white]⚗️  CÁLCULO PASO A PASO — {id_muestra}[/bold white]",
        style="white"
    ))
    console.print()
    console.print("[dim italic]  Fórmula: meq/L = (mg/L ÷ Peso Molecular) × Valencia[/dim]\n")
    
    # Simular procesamiento
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[cyan]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        tarea = progress.add_task("Convirtiendo unidades y calculando...", total=None)
        time.sleep(0.8)
    
    # Tablas de conversión
    cationes_meq = mostrar_tabla_conversion(cationes_datos, "Cationes")
    console.print()
    aniones_meq  = mostrar_tabla_conversion(aniones_datos,  "Aniones")
    console.print()
    
    # Balance
    resultado = calcular_balance(cationes_meq, aniones_meq)
    mostrar_resultado_balance(resultado, id_muestra)
    
    # Agregar datos completos al resultado para el resumen
    resultado["id_muestra"]    = id_muestra
    resultado["cationes_meq"]  = cationes_meq
    resultado["aniones_meq"]   = aniones_meq
    resultado["cationes_datos"] = cationes_datos
    resultado["aniones_datos"]  = aniones_datos
    
    return resultado


def mostrar_resumen_multiple(resultados: list):
    """
    Muestra una tabla resumen comparativa cuando se analizaron múltiples muestras.

    Parámetros
    ----------
    resultados : list de dicts (salida de procesar_y_mostrar_muestra)
    """
    if len(resultados) < 2:
        return
    
    console.print()
    console.print(Rule("[bold white]📋 RESUMEN COMPARATIVO DE TODAS LAS MUESTRAS[/bold white]", style="white"))
    console.print()
    
    tabla = Table(
        title="[bold white]Balance de Cargas — Comparativo[/bold white]",
        box=box.DOUBLE_EDGE,
        border_style="white",
        header_style="bold white",
        padding=(0, 1),
    )
    
    tabla.add_column("ID Muestra",  style="bold cyan",   justify="center", min_width=14)
    tabla.add_column("ΣCat (meq/L)", style="cyan",       justify="right",  min_width=13)
    tabla.add_column("ΣAni (meq/L)", style="magenta",    justify="right",  min_width=13)
    tabla.add_column("CBE (%)",      justify="right",     min_width=10)
    tabla.add_column("Evaluación",   justify="center",    min_width=14)
    tabla.add_column("Barra",        justify="left",      min_width=22)
    
    for r in resultados:
        cbe   = r["cbe"]
        eval_ = r["evaluacion"]
        abs_c = abs(cbe)
        color = "green" if abs_c < 5 else "red" if abs_c > 10 else "yellow"
        icono = "✅" if eval_ == "ACEPTABLE" else "❌"
        barra_n = min(int(abs_c * 1.5), 20)
        barra = f"[{color}]{'█' * barra_n}[/{color}][dim]{'░' * (20 - barra_n)}[/dim]"
        
        tabla.add_row(
            r["id_muestra"],
            f"{r['suma_cationes']:.3f}",
            f"{r['suma_aniones']:.3f}",
            f"[{color}]{cbe:+.2f}[/{color}]",
            f"[{color}]{icono} {eval_}[/{color}]",
            barra,
        )
    
    console.print(tabla)
    
    # Estadísticas rápidas
    total       = len(resultados)
    aceptables  = sum(1 for r in resultados if r["evaluacion"] == "ACEPTABLE")
    rechazados  = total - aceptables
    
    console.print()
    console.print(
        f"  [bold white]Muestras analizadas:[/bold white] {total}   "
        f"[bold green]✅ Aceptables: {aceptables}[/bold green]   "
        f"[bold red]❌ Rechazadas: {rechazados}[/bold red]"
    )
    console.print()


def leer_csv(ruta_archivo: str) -> list:
    """
    Lee muestras desde un archivo CSV.

    Formato esperado del CSV (encabezado en primera fila):
        ID,Na,K,Ca,Mg,Li,Cl,F,SO4,PO4,HCO3,CO3

    Parámetros
    ----------
    ruta_archivo : str  Ruta al archivo CSV

    Retorna
    -------
    list de dicts: [{id, Na, K, Ca, Mg, Li, Cl, F, SO4, PO4, HCO3, CO3}, ...]
    """
    muestras = []
    
    # Mapeo de columnas CSV → iones del programa
    mapa_columnas = {
        # Cationes
        "Na"  : ("cationes", "Na⁺"),
        "K"   : ("cationes", "K⁺"),
        "Ca"  : ("cationes", "Ca²⁺"),
        "Mg"  : ("cationes", "Mg²⁺"),
        "Li"  : ("cationes", "Li⁺"),
        # Aniones
        "Cl"  : ("aniones", "Cl⁻"),
        "F"   : ("aniones", "F⁻"),
        "SO4" : ("aniones", "SO₄²⁻"),
        "PO4" : ("aniones", "PO₄³⁻"),
        "HCO3": ("aniones", "HCO₃⁻"),
        "CO3" : ("aniones", "CO₃²⁻"),
    }
    
    try:
        with open(ruta_archivo, newline="", encoding="utf-8-sig") as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            
            for num_fila, fila in enumerate(lector, start=2):
                id_muestra = fila.get("ID", fila.get("id", f"Fila_{num_fila}")).strip()
                
                cationes_datos = []
                for simbolo, info in CATIONES.items():
                    # Buscar la columna correspondiente en el CSV
                    col_csv = next(
                        (k for k, v in mapa_columnas.items() if v == ("cationes", simbolo)),
                        None
                    )
                    mg_L = float(fila.get(col_csv, 0) or 0) if col_csv else 0.0
                    cationes_datos.append({
                        "simbolo" : simbolo,
                        "nombre"  : info["nombre"],
                        "pm"      : info["pm"],
                        "valencia": info["valencia"],
                        "mg_L"    : mg_L,
                    })
                
                aniones_datos = []
                for simbolo, info in ANIONES.items():
                    col_csv = next(
                        (k for k, v in mapa_columnas.items() if v == ("aniones", simbolo)),
                        None
                    )
                    mg_L = float(fila.get(col_csv, 0) or 0) if col_csv else 0.0
                    aniones_datos.append({
                        "simbolo" : simbolo,
                        "nombre"  : info["nombre"],
                        "pm"      : info["pm"],
                        "valencia": info["valencia"],
                        "mg_L"    : mg_L,
                    })
                
                muestras.append({
                    "id"             : id_muestra,
                    "cationes_datos" : cationes_datos,
                    "aniones_datos"  : aniones_datos,
                })
        
        return muestras
    
    except FileNotFoundError:
        console.print(f"  [red]✗  Archivo no encontrado: {ruta_archivo}[/red]")
        return []
    except Exception as e:
        console.print(f"  [red]✗  Error al leer CSV: {e}[/red]")
        return []


def exportar_resultados_csv(resultados: list, ruta_salida: str):
    """
    Exporta los resultados del balance a un CSV de resumen.

    Parámetros
    ----------
    resultados   : list de dicts con resultados
    ruta_salida  : str  Ruta del archivo de salida
    """
    encabezados = [
        "ID_Muestra", "Na_mgL", "K_mgL", "Ca_mgL", "Mg_mgL", "Li_mgL",
        "Cl_mgL", "F_mgL", "SO4_mgL", "PO4_mgL", "HCO3_mgL", "CO3_mgL",
        "SumaCationes_meqL", "SumaAniones_meqL", "CBE_%", "Evaluacion"
    ]
    
    ion_cat_order = ["Na⁺", "K⁺", "Ca²⁺", "Mg²⁺", "Li⁺"]
    ion_ani_order = ["Cl⁻", "F⁻", "SO₄²⁻", "PO₄³⁻", "HCO₃⁻", "CO₃²⁻"]
    
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=encabezados)
        escritor.writeheader()
        
        for r in resultados:
            # Construir mapa mg/L por símbolo
            cat_mgL = {d["simbolo"]: d["mg_L"] for d in r["cationes_datos"]}
            ani_mgL = {d["simbolo"]: d["mg_L"] for d in r["aniones_datos"]}
            
            fila = {
                "ID_Muestra"          : r["id_muestra"],
                "Na_mgL"              : cat_mgL.get("Na⁺",   0),
                "K_mgL"               : cat_mgL.get("K⁺",    0),
                "Ca_mgL"              : cat_mgL.get("Ca²⁺",  0),
                "Mg_mgL"              : cat_mgL.get("Mg²⁺",  0),
                "Li_mgL"              : cat_mgL.get("Li⁺",   0),
                "Cl_mgL"              : ani_mgL.get("Cl⁻",   0),
                "F_mgL"               : ani_mgL.get("F⁻",    0),
                "SO4_mgL"             : ani_mgL.get("SO₄²⁻", 0),
                "PO4_mgL"             : ani_mgL.get("PO₄³⁻", 0),
                "HCO3_mgL"            : ani_mgL.get("HCO₃⁻", 0),
                "CO3_mgL"             : ani_mgL.get("CO₃²⁻", 0),
                "SumaCationes_meqL"   : round(r["suma_cationes"], 4),
                "SumaAniones_meqL"    : round(r["suma_aniones"],  4),
                "CBE_%"               : round(r["cbe"], 4),
                "Evaluacion"          : r["evaluacion"],
            }
            escritor.writerow(fila)
    
    console.print(f"  [green]✓  Resultados exportados a:[/green] [bold white]{ruta_salida}[/bold white]")


def menu_principal() -> str:
    """
    Muestra el menú principal y retorna la opción elegida.

    Retorna
    -------
    str : '1', '2', o '3'
    """
    console.print(Panel(
        "[bold white]¿Cómo desea ingresar los datos?[/bold white]\n\n"
        "  [bold cyan][1][/bold cyan]  Ingresar una muestra manualmente (interactivo)\n"
        "  [bold cyan][2][/bold cyan]  Analizar múltiples muestras (manualmente, una por una)\n"
        "  [bold cyan][3][/bold cyan]  Cargar datos desde un archivo [bold]CSV[/bold]\n"
        "  [bold red][4][/bold red]  Salir",
        title="[bold white]🗂  MENÚ PRINCIPAL[/bold white]",
        border_style="cyan",
        padding=(1, 3),
    ))
    
    while True:
        opcion = Prompt.ask(
            "  [bold white]Seleccione una opción[/bold white]",
            choices=["1", "2", "3", "4"],
            console=console
        )
        return opcion


def mostrar_formato_csv():
    """Muestra al usuario el formato requerido para el CSV."""
    console.print(Panel(
        "[bold white]📄 FORMATO DEL ARCHIVO CSV[/bold white]\n\n"
        "El archivo debe tener una fila de encabezado y los siguientes campos:\n\n"
        "[cyan]ID,Na,K,Ca,Mg,Li,Cl,F,SO4,PO4,HCO3,CO3[/cyan]\n\n"
        "[dim]Ejemplo:[/dim]\n"
        "[dim]ID,Na,K,Ca,Mg,Li,Cl,F,SO4,PO4,HCO3,CO3[/dim]\n"
        "[dim]SF11,14000,1636,2411,222,27,27935,41,529,0,647,0[/dim]\n"
        "[dim]SF22,13550,1768,1460,315,62,25500,2,380,0,475,0[/dim]\n\n"
        "[yellow]• Valores en mg/L\n"
        "• Separador: coma (,)\n"
        "• Use 0 para iones no detectados[/yellow]",
        border_style="yellow",
        padding=(1, 3),
    ))
    console.print()


# =============================================================================
#  FUNCIÓN PRINCIPAL — Punto de entrada
# =============================================================================

def main():
    """
    Punto de entrada principal del programa.
    Controla el flujo general y el bucle de análisis de muestras.
    """
    mostrar_bienvenida()
    
    # Preguntar si desea ver la teoría
    ver_teoria = Confirm.ask(
        "  [dim]¿Desea ver el fundamento teórico antes de comenzar?[/dim]",
        default=False,
        console=console
    )
    if ver_teoria:
        mostrar_teoria()
    
    resultados_acumulados = []
    
    while True:
        console.print()
        opcion = menu_principal()
        
        # ── Opción 4: Salir ──────────────────────────────────────────────────
        if opcion == "4":
            if resultados_acumulados:
                mostrar_resumen_multiple(resultados_acumulados)
                
                exportar = Confirm.ask(
                    "  [dim]¿Desea exportar todos los resultados a un CSV?[/dim]",
                    default=True,
                    console=console
                )
                if exportar:
                    nombre_archivo = f"resultados_balance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    exportar_resultados_csv(resultados_acumulados, nombre_archivo)
            
            console.print()
            console.print(Panel(
                "[bold cyan]¡Hasta pronto! 👋[/bold cyan]\n\n"
                "[dim]Recuerde: un buen balance de cargas es el primer paso\n"
                "para una interpretación hidrogeoquímica confiable.[/dim]",
                border_style="cyan",
                padding=(1, 3),
            ))
            console.print()
            sys.exit(0)
        
        # ── Opción 3: CSV ────────────────────────────────────────────────────
        elif opcion == "3":
            mostrar_formato_csv()
            ruta = Prompt.ask(
                "  [bold white]Ruta del archivo CSV[/bold white]",
                console=console
            ).strip().strip('"').strip("'")
            
            console.print()
            muestras_csv = leer_csv(ruta)
            
            if not muestras_csv:
                console.print("  [red]No se pudieron cargar muestras del archivo.[/red]")
                continue
            
            console.print(f"  [green]✓  Se cargaron [bold]{len(muestras_csv)}[/bold] muestras del CSV.[/green]\n")
            
            for muestra in muestras_csv:
                resultado = procesar_y_mostrar_muestra(
                    muestra["id"],
                    muestra["cationes_datos"],
                    muestra["aniones_datos"]
                )
                resultados_acumulados.append(resultado)
                
                if len(muestras_csv) > 1:
                    continuar = Confirm.ask(
                        "  [dim]¿Ver siguiente muestra?[/dim]",
                        default=True,
                        console=console
                    )
                    if not continuar:
                        break
            
            mostrar_resumen_multiple(resultados_acumulados)
        
        # ── Opciones 1 y 2: Manual ───────────────────────────────────────────
        else:
            while True:
                id_m, cationes_d, aniones_d = capturar_muestra_interactiva()
                resultado = procesar_y_mostrar_muestra(id_m, cationes_d, aniones_d)
                resultados_acumulados.append(resultado)
                
                if opcion == "1":
                    break  # Solo una muestra en la opción 1
                
                # Opción 2: preguntar si analizar otra
                otra = Confirm.ask(
                    "  [dim]¿Desea analizar otra muestra?[/dim]",
                    default=True,
                    console=console
                )
                if not otra:
                    break
            
            if len(resultados_acumulados) > 1:
                mostrar_resumen_multiple(resultados_acumulados)
        
        # Preguntar si continuar en el menú principal
        console.print()
        volver = Confirm.ask(
            "  [dim]¿Volver al menú principal?[/dim]",
            default=True,
            console=console
        )
        if not volver:
            mostrar_resumen_multiple(resultados_acumulados)
            
            if resultados_acumulados:
                exportar = Confirm.ask(
                    "  [dim]¿Exportar resultados a CSV?[/dim]",
                    default=True,
                    console=console
                )
                if exportar:
                    nombre_archivo = f"resultados_balance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    exportar_resultados_csv(resultados_acumulados, nombre_archivo)
            
            console.print(Panel(
                "[bold cyan]¡Hasta pronto! 👋[/bold cyan]",
                border_style="cyan", padding=(1, 3)
            ))
            console.print()
            sys.exit(0)


# =============================================================================
#  EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n  [yellow]⚠  Programa interrumpido por el usuario.[/yellow]\n")
        sys.exit(0)

# -*- coding: utf-8 -*-%
"""
Created on %(date)s

@author: Diyar Altinses, M.Sc.

to-do:
    - 
"""

# %% imports

import numpy as np
from matplotlib import pyplot as plt
from distutils.spawn import find_executable
import numpy_financial as npf

# %%

def configure_plt(check_latex = True):
        """
        Set Font sizes for plots.
    
        Parameters
        ----------
        check_latex : bool, optional
            Use LaTex-mode (if available). The default is True.
    
        Returns
        -------
        None.
    
        """
        
        if check_latex:
            
            if find_executable('latex'):
                plt.rc('text', usetex=True)
            else:
                plt.rc('text', usetex=False)
        plt.rc('font',family='Times New Roman')
        plt.rcParams.update({'figure.max_open_warning': 0})
        
        small_size = 13
        small_medium = 14
        medium_size = 16
        big_medium = 18
        big_size = 20
        
        plt.rc('font', size = small_size)          # controls default text sizes
        plt.rc('axes', titlesize = big_medium)     # fontsize of the axes title
        plt.rc('axes', labelsize = medium_size)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize = small_size)    # fontsize of the tick labels
        plt.rc('ytick', labelsize = small_size)    # fontsize of the tick labels
        plt.rc('legend', fontsize = small_medium)    # legend fontsize
        plt.rc('figure', titlesize = big_size)  # fontsize of the figure title
        
        plt.rc('grid', c='0.5', ls='-', lw=0.5)
        plt.grid(True)
        plt.tight_layout()
        plt.close()
        
#%% config

configure_plt()

# %% params

# Kreditparameter
kreditsumme = 500000  # Euro
zinssatz_kredit_ = 0.025  # 3% p.a.
tilgung_prozent = 0.02
zinssatz_kredit = zinssatz_kredit_ + tilgung_prozent
laufzeit = 30  # Jahre (geplante Tilgungsdauer)
zusatz_geld = 10000  # Zusätzliche 10.000 € pro Jahr (für Sondertilgung oder ETF)
etf_rendite = 0.07  # ETF-Parameter

# %% Simulation über 20 Jahre

annuitaet = npf.pmt(zinssatz_kredit, laufzeit, -kreditsumme)
print(f"Jährliche Annuität (regulär): {annuitaet:.2f} €")
jahre = np.arange(1, laufzeit + 1)

# %% Szenario 1: Mit Sondertilgung (10.000 € extra pro Jahr)
restschuld_sondertilgung = [kreditsumme]
zinsen_sondertilgung = []
tilgung_sondertilgung = []

for j in range(1, laufzeit + 1):
    zinsen = restschuld_sondertilgung[-1] * zinssatz_kredit
    tilgung_regulaer = annuitaet - zinsen
    tilgung_gesamt = tilgung_regulaer + zusatz_geld  # Sondertilgung!
    
    neue_restschuld = restschuld_sondertilgung[-1] - tilgung_gesamt
    if neue_restschuld < 0:
        neue_restschuld = 0
    restschuld_sondertilgung.append(neue_restschuld)
    zinsen_sondertilgung.append(zinsen)
    tilgung_sondertilgung.append(tilgung_gesamt)
    
    if neue_restschuld == 0:
        break

# %% Szenario 2: Ohne Sondertilgung (10.000 € in ETF)

restschuld_ohne_sondertilgung = [kreditsumme]
etf_portfolio = [0]
zinsen_ohne_sondertilgung = []

for j in range(1, laufzeit + 1):
    # Kredit (reguläre Annuität)
    zinsen = restschuld_ohne_sondertilgung[-1] * zinssatz_kredit
    tilgung_regulaer = annuitaet - zinsen
    neue_restschuld = restschuld_ohne_sondertilgung[-1] - tilgung_regulaer
    restschuld_ohne_sondertilgung.append(neue_restschuld)
    zinsen_ohne_sondertilgung.append(zinsen)
    
    # ETF
    if j == 1:
        etf_wert = zusatz_geld
    else:
        etf_wert = etf_portfolio[-1] * (1 + etf_rendite) + zusatz_geld
    etf_portfolio.append(etf_wert)

# %% Break-Even-Point: Wann übersteigt ETF-Wert die Restschuld mit Sondertilgung?

break_even_jahr = None
for j in range(1, min(len(restschuld_ohne_sondertilgung), len(etf_portfolio))):
    if etf_portfolio[j] > restschuld_ohne_sondertilgung[j]:
        break_even_jahr = j
        break

# %% Wann ist der Kredit jeweils abbezahlt?

jahr_abbezahlt_sondertilgung = np.argmin(np.array(restschuld_sondertilgung) > 0) if min(restschuld_sondertilgung) <= 0 else laufzeit
jahr_abbezahlt_ohne = np.argmin(np.array(restschuld_ohne_sondertilgung) > 0) if min(restschuld_ohne_sondertilgung) <= 0 else laufzeit

# %% Plot

plt.figure(figsize=(6, 4))
plt.plot(range(len(restschuld_sondertilgung)), restschuld_sondertilgung, label='Mit Sondertilgung', color='blue')
plt.plot(range(len(etf_portfolio)), etf_portfolio, label='ETF-Portfolio', color='green')
plt.plot(range(len(restschuld_ohne_sondertilgung)), restschuld_ohne_sondertilgung, label='Ohne Sondertilgung', linestyle='--', color='red')

if break_even_jahr:
    plt.axvline(x=break_even_jahr, color='gray', linestyle='--', label=f'Break-Even (Jahr {break_even_jahr})')
    plt.axhline(y=restschuld_sondertilgung[break_even_jahr], color='gray', linestyle=':')

plt.xlabel('Jahr')
plt.ylabel('Betrag (€)')
plt.legend()
plt.grid(True)
plt.ylim(0,600000)
plt.tight_layout()
plt.savefig('kredit.png', dpi = 300, bbox_inches = 'tight')
plt.show()

# Ergebnisse ausgeben
print("\n--- Ergebnisse ---")
print(f"Reguläre Annuität (ohne Sondertilgung): {annuitaet:.2f} € pro Jahr")
print(f"Mit Sondertilgung: Kredit abbezahlt in Jahr {jahr_abbezahlt_sondertilgung}")
print(f"Ohne Sondertilgung: Kredit abbezahlt in Jahr {jahr_abbezahlt_ohne}")

if break_even_jahr:
    print(f"\nBreak-Even-Point in Jahr {break_even_jahr}:")
    print(f"  - Restschuld mit Sondertilgung: {restschuld_sondertilgung[break_even_jahr]:.2f} €")
    print(f"  - ETF-Portfolio: {etf_portfolio[break_even_jahr]:.2f} €")
else:
    print("\nKein Break-Even-Point innerhalb der Laufzeit erreicht.")

# Netto-Vergleich am Ende der Laufzeit
netto_sondertilgung = -restschuld_sondertilgung[-1]  # 0, da abbezahlt
netto_etf = etf_portfolio[-1] - restschuld_ohne_sondertilgung[-1]

print(f"\nNetto-Vermögen nach {laufzeit} Jahren:")
print(f"Mit Sondertilgung: {netto_sondertilgung:.2f} € (Kredit abbezahlt)")
print(f"Mit ETF-Investition: {netto_etf:.2f} € (ETF - Restschuld)")
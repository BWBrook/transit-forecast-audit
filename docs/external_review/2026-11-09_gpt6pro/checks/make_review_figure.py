#!/usr/bin/env python3
"""Draw a review diagnostic from actual saved timings, not synthetic data.

The right panel shows latent forecast intervals implied by frozen M0/M2,
excluding measurement error. This is illustrative, not an observing scheduler.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from recompute_review import half_width

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True)
    a=p.parse_args();e=a.evidence
    result=json.loads((e/'review_check_results.json').read_text())
    h=pd.read_csv(e/'hr858b_review.csv',float_precision='round_trip')
    w=pd.read_csv(a.repo/'data/derived/final_primary/measured/windows.csv.gz',float_precision='round_trip')
    l=pd.read_csv(a.repo/'results/final_primary/terminal_ledger.csv.gz')
    f=pd.read_csv(a.repo/'results/prefreeze/forecasts_core_draft.csv.gz',float_precision='round_trip')
    h=l[(l.planet=='HR858b') & (l.status=='accepted')].merge(w,left_on='window_event_id',right_on='event_id',suffixes=('','_window'))
    h=h.merge(f[['event_id','forecast_variance_s2','predicted_bjd_tdb','M2_s_log_lambda']],on='event_id').sort_values('forecast_epoch')
    epoch=h.forecast_epoch.to_numpy();sd=np.sqrt(h.forecast_variance_s2.to_numpy());s=float(h.M2_s_log_lambda.iloc[0])
    q0=np.array([half_width(v,0,1,0) for v in h.forecast_variance_s2])/60
    q2=np.array([half_width(v,0,1,s) for v in h.forecast_variance_s2])/60
    fig,axs=plt.subplots(1,2,figsize=(12.5,4.7),layout='constrained',gridspec_kw={'width_ratios':[1,1.35]})
    colors={'M0':'#426579','M1':'#996b35','M2':'#137e83','M3':'#9b63a5'}
    for m in ['M0','M1','M2','M3']:
        x=result['summary']['width95_minutes'][m]['mean'];y=100*result['summary']['covered95'][m]['mean']
        axs[0].scatter(x,y,s=65,color=colors[m],zorder=3)
        offsets={'M0':(6,-14),'M1':(-30,-17),'M2':(-31,-13),'M3':(9,3)}
        axs[0].annotate(m,(x,y),xytext=offsets[m],textcoords='offset points',fontsize=11,color=colors[m],weight='bold')
    axs[0].axhline(95,color='#555555',ls='--',lw=1,label='Nominal 95%')
    axs[0].set(xlabel='Mean interval width (minutes)',ylabel='Measured-time coverage (%)',ylim=(88,101),xlim=(0,65),title='Coverage rises as intervals widen')
    axs[0].legend(loc='lower right',frameon=False,fontsize=9)
    axs[0].text(.02,.97,'151 planets; equal planet weights\nConvolved measured-time intervals',transform=axs[0].transAxes,va='top',fontsize=9)
    axs[1].fill_between(epoch,-q2,q2,color=colors['M2'],alpha=.22,label='M2 latent 95% interval')
    axs[1].fill_between(epoch,-q0,q0,color=colors['M0'],alpha=.35,label='M0 latent 95% interval')
    residual=(h.tc_bjd_tdb-h.predicted_bjd_tdb)*1440
    axs[1].errorbar(epoch,residual,yerr=np.array([-h.q025_s,h.q975_s])/60,fmt='o',ms=4,color='#322d39',capsize=2,label='Saved timings + reported 95% limits')
    axs[1].axhline(0,color='#555555',lw=.8)
    axs[1].set(xlabel='Transit number in the issued ephemeris',ylabel='Time relative to issued prediction (minutes)',ylim=(-445,115),title='HR 858 b: the dominant score gain still misses')
    axs[1].legend(loc='center right',frameon=False,fontsize=8)
    axs[1].text(.02,.25,'16 accepted events; all outside both measured-time 95% intervals\nLatent bands shown here exclude measurement uncertainty.',transform=axs[1].transAxes,fontsize=8.6,va='bottom')
    for ax in axs:
        ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.15,zorder=0)
    fig.suptitle('Review diagnostics • frozen experiment preserved',fontsize=14)
    fig.savefig(e/'review_diagnostics.png',dpi=190)
    fig.savefig(e/'review_diagnostics.pdf')
    print(str(e/'review_diagnostics.png'))

if __name__=='__main__':main()

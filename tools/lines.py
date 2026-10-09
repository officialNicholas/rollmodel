import subprocess, os
S='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
V=S+'/voice'; LUDO=S+'/tools/ludo.py'; SAMPLE=V+'/announcer_a.mp3'
LINES=[('go','Three! Two! One! GO!'),('victory','Victory!'),('defeat','Defeat!'),('draw','It\'s a draw!'),('time','Time\'s up!'),('best','New best!'),('title','Roll Model!'),('ready','Get ready to roll!'),('levelup','Level up!'),('welcome','Welcome back!')]
for k,t in LINES:
    out=f'{V}/say_{k}.mp3'
    if os.path.exists(out): continue
    r=subprocess.run(['python3','-I',LUDO,'speech',out,SAMPLE,t,'--rid','rm5-say-'+k],capture_output=True,text=True)
    print(k,'ok' if r.returncode==0 else 'FAIL',(r.stderr.strip().splitlines() or [''])[-1][:160],flush=True)

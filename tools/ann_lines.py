import subprocess, os, sys
S='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
LA=S+'/la/voice'; LUDO=S+'/tools/ludo.py'; SAMPLE=LA+'/ann_c.mp3'
LINES=[('go','GO!'),('cd3','Three!'),('cd2','Two!'),('cd1','One!'),('ready',"Are you ready? Let's ROLL!"),('victory','VICTORY!'),('defeat','Defeat!'),('draw',"It's a draw!"),('time',"Time's up!"),('best','New best!'),('title','Roll Model!'),('levelup','Level up!'),('welcome','Welcome back, champ!'),('final','Final seconds!')]
for k,t in LINES:
    out=f'{LA}/say_{k}.mp3'
    if os.path.exists(out): continue
    r=subprocess.run(['python3','-I',LUDO,'speech',out,SAMPLE,t,'--rid','rm7-say-c-'+k],capture_output=True,text=True)
    print(k,'ok' if r.returncode==0 else 'FAIL',(r.stderr.strip().splitlines() or [''])[-1][:160],flush=True)
print('lines done')

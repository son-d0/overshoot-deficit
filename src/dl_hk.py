"""Acquire HKG.IDX/HKD tick data from the Dukascopy datafeed.

All 24 UTC hours are requested. Level A of the pre-registration is the full tradable
window, and this instrument's window crosses midnight, so restricting to the day session
would not cover it.

The date range matches the VN30F1M discovery sample exactly, 2021-02-25 to 2026-08-26.
That is a constraint inherited from the discovery study, not a choice made here.

Five threads with exponential backoff; the server is slow rather than rate-generous.
Files are cached on disk, so re-running fetches only what is missing. An empty file is
written for an hour the instrument does not quote, so it is not requested again."""
import urllib.request,urllib.error,os,time,datetime as dt,threading,ssl
from concurrent.futures import ThreadPoolExecutor

# A fresh virtual environment on macOS often has no usable certificate store, and urllib then
# fails every request with CERTIFICATE_VERIFY_FAILED. Retrying cannot fix that, so use certifi's
# bundle when it is installed and say so plainly when it is not.
try:
    import certifi; CTX=ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX=ssl.create_default_context()
INST='HKGIDXHKD'; ROOT='raw'; W=5
D0=dt.date(2021,2,25); D1=dt.date(2026,8,26)
UA={'User-Agent':'Mozilla/5.0 (academic research; directional-change study)'}

jobs=[]; d=D0
while d<=D1:
    if d.weekday()<5:
        for h in range(0,24):
            p=f'{ROOT}/{d:%Y/%m/%d}/{h:02d}h.bi5'
            if not os.path.exists(p): jobs.append((d,h,p))
    d+=dt.timedelta(days=1)
tot=len(jobs); lk=threading.Lock(); done=[0]; ok=[0]; emp=[0]; bad=[0]; t0=time.time()
print(f'{tot:,} files to fetch',flush=True)

def one(job):
    d,h,p=job
    u=f'https://datafeed.dukascopy.com/datafeed/{INST}/{d.year}/{d.month-1:02d}/{d.day:02d}/{h:02d}h_ticks.bi5'
    b=None
    for k in range(7):
        try:
            b=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90,context=CTX).read(); break
        except urllib.error.HTTPError as e:
            if e.code==404: b=b''; break
            time.sleep(min(2.0*(2**k),40))
        except ssl.SSLCertVerificationError:
            # Not transient. Every later request would fail the same way.
            raise SystemExit(
                'TLS certificate verification failed against the Dukascopy feed.\n'
                'This is a local certificate-store problem, not a problem with the data source,\n'
                'and retrying will not clear it. Install certifi (pip install certifi) and run\n'
                'again, or on macOS run the "Install Certificates.command" that ships with Python.')
        except Exception:
            time.sleep(min(1.5*(2**k),40))
    with lk:
        done[0]+=1
        if b is None: bad[0]+=1
        else:
            os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(b)
            (ok if b else emp)[0]+=1
        if done[0]%50==0:
            el=time.time()-t0; r=done[0]/el
            print(f'{done[0]:,}/{tot:,}  ok={ok[0]:,} empty={emp[0]:,} failed={bad[0]:,}  '
                  f'{r:.2f} files/s  ~{(tot-done[0])/max(r,1e-9)/60:.0f} min remaining',flush=True)
with ThreadPoolExecutor(W) as ex: list(ex.map(one,jobs))
print(f'DONE ok={ok[0]:,} empty={emp[0]:,} failed={bad[0]:,}  {(time.time()-t0)/60:.1f} min',flush=True)

function toggleSide(){document.getElementById('side')?.classList.toggle('open')}
function toast(msg){let x=document.createElement('div');x.className='toast';x.textContent=msg;document.body.appendChild(x);setTimeout(()=>x.remove(),2600)}

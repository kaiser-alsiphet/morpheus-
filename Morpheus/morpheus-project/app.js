const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],rm=matchMedia("(prefers-reduced-motion:reduce)").matches;
addEventListener("load",()=>setTimeout(()=>$("#load").classList.add("done"),500));
const h=$("#h1");h.innerHTML=h.textContent.split(" ").map((w,i)=>`<span class="w"><b style="transition-delay:${i*.08}s">${w}</b></span>`).join(" ");
const io=new IntersectionObserver(es=>es.forEach(e=>e.isIntersecting&&(e.target.classList.add("in"),io.unobserve(e.target))),{threshold:.15});$$(".rv").forEach(e=>io.observe(e));
const px=$(".px svg");addEventListener("scroll",()=>{const d=document.documentElement;$("#bar").style.width=scrollY/(d.scrollHeight-innerHeight)*100+"%";if(!rm)px.style.transform=`translateY(${-Math.min(scrollY,600)*.08}px)`},{passive:true});
const nb=$("#nb"),close=()=>{$("#nav").classList.remove("open");nb.setAttribute("aria-expanded","false")};
nb.onclick=()=>{const o=nb.getAttribute("aria-expanded")!=="true";nb.setAttribute("aria-expanded",o);$("#nav").classList.toggle("open",o)};
$$("nav a").forEach(a=>a.addEventListener("click",close));addEventListener("keydown",e=>e.key==="Escape"&&close());
if(matchMedia("(pointer:fine)").matches&&!rm){document.body.classList.add("cc");const c=$("#cur");let x=0,y=0,tx=0,ty=0,vx=0,vy=0;
addEventListener("mousemove",e=>{tx=e.clientX;ty=e.clientY});
(function loop(){vx+=(tx-x)*.12;vy+=(ty-y)*.12;vx*=.72;vy*=.72;x+=vx;y+=vy;const v=Math.min(Math.hypot(vx,vy)/18,.6),a=Math.atan2(vy,vx)*180/Math.PI;
c.style.transform=`translate(${x}px,${y}px) rotate(${a}deg) scale(${1+v},${1-v*.5})`;requestAnimationFrame(loop)})();
$$("a,button,summary,input").forEach(e=>{e.onmouseenter=()=>c.classList.add("h");e.onmouseleave=()=>c.classList.remove("h")});
$$(".mag").forEach(b=>{b.addEventListener("mousemove",e=>{const r=b.getBoundingClientRect();b.style.transform=`translate(${(e.clientX-r.left-r.width/2)*.3}px,${(e.clientY-r.top-r.height/2)*.4}px) scale(1.07,.95)`});b.addEventListener("mouseleave",()=>b.style.transform="")})}
const ok=$("#ok"),go=$("#go");ok.onchange=()=>go.setAttribute("aria-disabled",!ok.checked);
go.onclick=e=>{e.preventDefault();if(!ok.checked){ok.focus();return}document.body.classList.add("leaving");setTimeout(()=>location.href=go.href,300)};
$("#df").onsubmit=e=>{e.preventDefault();location.href=`mailto:contact@example.com?subject=Data%20deletion%20request&body=Please%20delete%20data%20linked%20to%20${encodeURIComponent($("#em").value)}.`;$("#dm").textContent="Your email app should open. Send the message to complete the request."};
const ck=$("#ck");let s=null;try{s=localStorage.getItem("cc")}catch(e){}if(!s)ck.hidden=false;
$$("#ck button").forEach(b=>b.onclick=()=>{try{localStorage.setItem("cc",b.dataset.c)}catch(e){}ck.hidden=true});

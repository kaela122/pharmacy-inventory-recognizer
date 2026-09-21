import { useEffect, useState } from "react";
import Sidebar, { NAV } from "./components/Sidebar";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import MedicinesPage from "./pages/MedicinesPage";
import CategoriesPage from "./pages/CategoriesPage";
import OrdersPage from "./pages/OrdersPage";
import SuppliersPage from "./pages/SuppliersPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import RecognizerPage from "./pages/RecognizerPage";
import UsersPage from "./pages/UsersPage";
import { loadAuth, clearAuth, ROLE_LABEL, type AuthUser } from "./lib/auth";

const PAGES:Record<string,()=>JSX.Element> = {
  dashboard:DashboardPage, medicines:MedicinesPage, categories:CategoriesPage,
  orders:OrdersPage, suppliers:SuppliersPage, analytics:AnalyticsPage,
  recognizer:RecognizerPage, users:UsersPage,
};

export default function App(){
  const [auth,setAuth]=useState<AuthUser|null>(loadAuth());
  const [page,setPage]=useState("dashboard"); const [open,setOpen]=useState(false);
  const [now,setNow]=useState(new Date());
  useEffect(()=>{ const t=setInterval(()=>setNow(new Date()),30000); return ()=>clearInterval(t); },[]);
  if(!auth) return <LoginPage onLogin={setAuth}/>;

  const go=(k:string)=>{ setPage(k); setOpen(false); };
  const logout=()=>{ clearAuth(); setAuth(null); };
  const allowed = page!=="users" || auth.role==="admin";
  const Page=allowed?PAGES[page]:DashboardPage; const title=NAV.find(n=>n.key===page)?.label??"";
  const time=now.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"});
  const date=now.toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric"});
  return (
    <div className="app">
      <Sidebar page={page} go={go} open={open} onLogout={logout} user={auth}/>
      <main>
        <div className="topbar">
          <div style={{display:"flex",alignItems:"center",gap:12}}>
            <button className="burger" onClick={()=>setOpen(o=>!o)}>☰</button>
            <h1>{title}</h1>
          </div>
          <div className="right">
            <span className="rolepill">🛡 {ROLE_LABEL[auth.role]||auth.role} <span className="clk">{time}</span></span>
            <span>{date}</span>
            <span className="avatar">{auth.full_name.charAt(0)}</span>
          </div>
        </div>
        <div className="content"><Page/></div>
      </main>
    </div>
  );
}

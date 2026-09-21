import { loadAuth } from "../lib/auth";
const BASE = "/api";

async function req<T>(path:string, opts:RequestInit={}):Promise<T>{
  const auth = loadAuth();
  const headers:Record<string,string> = { "Content-Type":"application/json", ...(opts.headers as Record<string,string>||{}) };
  if(auth?.token) headers["Authorization"] = `Bearer ${auth.token}`;
  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if(!res.ok){
    let detail = `${res.status}`;
    try{ const j = await res.json(); detail = j.detail ?? detail; }catch{ /* ignore */ }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if(res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
export const apiGet = <T>(p:string) => req<T>(p);
export const apiPost = <T>(p:string, body:unknown) => req<T>(p,{method:"POST",body:JSON.stringify(body)});
export const apiPut  = <T>(p:string, body:unknown) => req<T>(p,{method:"PUT",body:JSON.stringify(body)});
export const apiDel  = (p:string) => req<void>(p,{method:"DELETE"});
export const apiPatch= <T>(p:string, body:unknown) => req<T>(p,{method:"PATCH",body:JSON.stringify(body)});

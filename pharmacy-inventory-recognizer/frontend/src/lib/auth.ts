const KEY = "pharmahub_auth";
export interface AuthUser { token:string; employee_id:string; full_name:string; role:string; }

export function saveAuth(a:AuthUser){ try{ localStorage.setItem(KEY, JSON.stringify(a)); }catch{} }
export function loadAuth():AuthUser|null{
  try{ const s=localStorage.getItem(KEY); return s?JSON.parse(s):null; }catch{ return null; }
}
export function clearAuth(){ try{ localStorage.removeItem(KEY); }catch{} }
export const ROLE_LABEL:Record<string,string> = {
  admin:"System Admin", inventory_manager:"Inventory Manager", pharmacist:"Pharmacist",
};

import { apiGet, apiPost, apiPut, apiDel, apiPatch } from "./client";
import type { Category, Product, ProductInput, Supplier, Order, OrderStats, Stats, Analytics } from "../types";
import type { AuthUser } from "../lib/auth";

export const login         = (employee_id:string,password:string) => apiPost<AuthUser>("/auth/login",{employee_id,password});
export const getStats      = () => apiGet<Stats>("/dashboard/stats");
export const getAnalytics  = () => apiGet<Analytics>("/dashboard/analytics");
export const getCategories = () => apiGet<Category[]>("/categories");
export const addCategory   = (name:string,description:string) => apiPost<Category>("/categories",{name,description});
export const delCategory   = (id:number) => apiDel(`/categories/${id}`);
export const getProducts   = () => apiGet<Product[]>("/products");
export const addProduct    = (p:ProductInput) => apiPost<Product>("/products",p);
export const editProduct   = (id:number,p:ProductInput) => apiPut<Product>(`/products/${id}`,p);
export const delProduct    = (id:number) => apiDel(`/products/${id}`);
export const getSuppliers  = () => apiGet<Supplier[]>("/suppliers");
export const getOrders     = () => apiGet<Order[]>("/orders");
export const getOrderStats = () => apiGet<OrderStats>("/orders/stats");
export const setOrderStatus = (id:number,status:string) => apiPatch<Order>(`/orders/${id}/status`,{status});
export const validateCode  = (code:string) => apiPost<{verdict:string}>("/recognizer/validate",{code});

import type { SupplierFull, SupplierInput, Movement, MovementInput, User, UserInput } from "../types";
export const getSuppliersFull = () => apiGet<SupplierFull[]>("/suppliers");
export const addSupplier   = (s:SupplierInput) => apiPost<SupplierFull>("/suppliers",s);
export const editSupplier  = (id:number,s:SupplierInput) => apiPut<SupplierFull>(`/suppliers/${id}`,s);
export const delSupplier   = (id:number) => apiDel(`/suppliers/${id}`);
export const recordMovement = (pid:number,m:MovementInput) => apiPost<Movement>(`/products/${pid}/movements`,m);
export const getHistory    = (pid:number) => apiGet<Movement[]>(`/products/${pid}/movements`);
export const getMovements  = () => apiGet<Movement[]>("/movements");
export const getUsers      = () => apiGet<User[]>("/users");
export const addUser       = (u:UserInput) => apiPost<User>("/users",u);
export const editUser      = (id:number,u:UserInput) => apiPut<User>(`/users/${id}`,u);
export const delUser       = (id:number) => apiDel(`/users/${id}`);

export type TheoryStep = { from:string; subset:string[]; symbol:string; move:string[]; closure:string[]; result:string; new:boolean };
export type Theory = {
  alphabet:string[]; regex:string; columns:string[];
  nfa:{ states:string[]; start:string; accepting:string[];
        rows:{ state:string; cells:Record<string,string[]>; eps:string[]; meaning:string }[] };
  subset:{ start:string; steps:TheoryStep[]; possible_subsets:number;
           states:{ name:string; subset:string[]; accepting:boolean; row:Record<string,string> }[] };
  minimization:{ unreachable:string[]; rounds:string[][][]; merged:string[][];
                 blocks:{ members:string[]; name:string }[];
                 states:{ name:string; row:Record<string,string>; accepting:boolean; start:boolean }[] };
  counts:{ nfa:number; dfa:number; min:number };
  matches_simulator:boolean;
  subset_names:Record<string,string[]>;
};
export const getTheory = () => apiGet<Theory>("/recognizer/theory");

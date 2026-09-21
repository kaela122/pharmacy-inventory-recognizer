export interface Product {
  product_id:number; sku:string; name:string; category_id:number|null; category_name:string|null;
  price:number; stock:number; reorder_level:number; status:string;
}
export interface ProductInput {
  sku:string; name:string; category_id:number|null; price:number; reorder_level:number; stock:number;
}
export interface Category {
  category_id:number; name:string; description:string; sku_count:number; units:number;
  value:number; alerts:number; products:Product[];
}
export interface Supplier { supplier_id:number; name:string; }
export interface OrderItem { sku:string; name:string; quantity:number; subtotal:number; }
export interface Order {
  order_id:number; order_number:string; supplier_name:string; status:string;
  order_date:string; item_count:number; total:number; items:OrderItem[];
}
export interface OrderStats { total_orders:number; pending:number; fulfilled:number; total_value:number; }
export interface Slice { label:string; value:number; }
export interface AlertItem { sku:string; name:string; stock:number; reorder_level:number; status:string; }
export interface Stats {
  total_units:number; medicine_skus:number; low_stock:number; out_of_stock:number;
  alerts:AlertItem[]; category_distribution:Slice[];
}
export interface Analytics {
  stock_by_category:Slice[]; value_by_category:Slice[]; status_distribution:Slice[]; restocking:AlertItem[];
}

export interface SupplierFull {
  supplier_id:number; name:string; contact_person:string; phone:string; email:string; order_count:number;
}
export interface SupplierInput { name:string; contact_person:string; phone:string; email:string; }
export interface Movement {
  movement_id:number; product_id:number; sku:string; product_name:string;
  movement_type:string; change:number; resulting_stock:number; note:string;
  employee_id:string; created_at:string;
}
export interface MovementInput { movement_type:string; quantity:number; note:string; }
export interface User { user_id:number; employee_id:string; full_name:string; role:string; }
export interface UserInput { employee_id:string; full_name:string; role:string; password:string; }

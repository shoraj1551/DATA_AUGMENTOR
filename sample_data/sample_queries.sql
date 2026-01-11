SELECT * FROM customers WHERE city = 'New York';

SELECT customer_id, SUM(order_amount) 
FROM orders 
GROUP BY customer_id;

SELECT c.name, o.order_date, o.amount
FROM customers c, orders o
WHERE c.id = o.customer_id;

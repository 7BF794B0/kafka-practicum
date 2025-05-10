-- Добавление пользователей
INSERT INTO public.users (name, email) VALUES ('John Doe', 'john@example.com');
INSERT INTO public.users (name, email) VALUES ('Jane Smith', 'jane@example.com');
INSERT INTO public.users (name, email) VALUES ('Alice Johnson', 'alice@example.com');
INSERT INTO public.users (name, email) VALUES ('Bob Brown', 'bob@example.com');
INSERT INTO public.users (name, email) VALUES ('Tom Smith', 'tom@example.com');

-- Добавление заказов
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (1, 'Product A', 2);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (1, 'Product B', 1);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (2, 'Product C', 3);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (2, 'Product D', 5);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (3, 'Product E', 2);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (3, 'Product F', 1);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (4, 'Product G', 3);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (4, 'Product H', 5);
INSERT INTO public.orders (user_id, product_name, quantity) VALUES (5, 'Product I', 2);

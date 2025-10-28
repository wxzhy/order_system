CREATE DATABASE IF NOT EXISTS ordersystem
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE ordersystem;

-- 1. 用户表 (user)
-- 基于: User类 - 支持管理员、商家、普通用户三种类型
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱地址',
    phone VARCHAR(50) UNIQUE COMMENT '联系电话',
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    user_type ENUM('customer', 'vendor', 'admin') NOT NULL DEFAULT 'customer' COMMENT '用户类型: customer(普通用户), vendor(商家), admin(管理员)',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_user_type (user_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 商家信息表 (store)
-- 基于: Store类
CREATE TABLE store (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商家ID',
    name VARCHAR(255) NOT NULL COMMENT '商家名称',
    description TEXT COMMENT '商家简介',
    address VARCHAR(255) NOT NULL COMMENT '商家地址',
    phone VARCHAR(50) NOT NULL COMMENT '联系电话',
    hours VARCHAR(100) COMMENT '营业时间',
    image_url VARCHAR(255) COMMENT '商家图片URL',
    state ENUM('pending', 'approved', 'disabled') NOT NULL DEFAULT 'pending' COMMENT '审核状态: pending(待审核), approved(正常营业), disabled(已停用)',
    publish_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    review_time DATETIME COMMENT '审核时间',
    owner_id INT NOT NULL COMMENT '商家所有者ID(关联user表)',
    FOREIGN KEY (owner_id) REFERENCES user(id) ON DELETE CASCADE,
    INDEX idx_name (name),
    INDEX idx_state (state),
    INDEX idx_owner_id (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商家信息表';

-- 3. 餐点信息表 (item)
-- 基于: Item类
CREATE TABLE item (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '餐点ID',
    name VARCHAR(255) NOT NULL COMMENT '餐点名称',
    description TEXT COMMENT '餐点简介',
    image_url VARCHAR(255) COMMENT '餐点图片URL',
    price DECIMAL(10, 2) NOT NULL COMMENT '价格',
    quantity INT NOT NULL DEFAULT 0 COMMENT '库存数量',
    store_id INT NOT NULL COMMENT '所属商家ID',
    FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE,
    INDEX idx_name (name),
    INDEX idx_store_id (store_id),
    INDEX idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='餐点信息表';

-- 4. 预约订单表 (order)
-- 基于: Order类
CREATE TABLE `order` (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    review_time DATETIME COMMENT '审核时间',
    state ENUM('pending', 'approved', 'completed', 'cancelled') NOT NULL DEFAULT 'pending' COMMENT '订单状态: pending(待审核), approved(已同意), completed(已完成), cancelled(已取消)',
    user_id INT NOT NULL COMMENT '用户ID',
    store_id INT NOT NULL COMMENT '商家ID',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_store_id (store_id),
    INDEX idx_state (state),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 5. 订单商品表 (orderitem)
-- 基于: OrderItem类
CREATE TABLE orderitem (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单项ID',
    order_id INT NOT NULL COMMENT '订单ID',
    item_id INT NOT NULL COMMENT '餐点ID',
    item_price DECIMAL(10, 2) NOT NULL COMMENT '下单时的餐点单价',
    quantity INT NOT NULL COMMENT '数量',
    FOREIGN KEY (order_id) REFERENCES `order`(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_item_id (item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单商品表';

-- 6. 评论表 (comment)
-- 基于: Comment类
CREATE TABLE comment (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评论ID',
    content TEXT NOT NULL COMMENT '评论内容',
    publish_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    review_time DATETIME COMMENT '审核时间',
    state ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending' COMMENT '审核状态: pending(未审核), approved(审核通过), rejected(审核未通过)',
    user_id INT NOT NULL COMMENT '评论者ID',
    store_id INT NOT NULL COMMENT '商家ID',
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES store(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_store_id (store_id),
    INDEX idx_state (state),
    INDEX idx_publish_time (publish_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- ============================================================
-- 插入初始测试数据
-- ============================================================

-- 1. 插入用户数据
-- 密码说明：
--   admin: 'admin123456' -> SHA256: ac0e7d037817094e9e0b4441f9bae3209d67b02fa484917065f71b16109a1a78
--   其他用户: 'password123' -> SHA256: ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
INSERT INTO user (username, email, phone, hashed_password, user_type, create_time) VALUES
('admin', 'admin@ordersystem.com', '10086', 'ac0e7d037817094e9e0b4441f9bae3209d67b02fa484917065f71b16109a1a78', 'admin', '2024-10-01 08:00:00'),
('vendor_zhang', 'zhang@example.com', '13800001111', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'vendor', '2024-10-01 09:00:00'),
('vendor_li', 'li@example.com', '13900002222', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'vendor', '2024-10-01 09:30:00'),
('customer_ming', 'ming@example.com', '18600003333', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'customer', '2024-10-02 10:00:00'),
('customer_hong', 'hong@example.com', '18600004444', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'customer', '2024-10-02 11:00:00');

-- 2. 插入商家信息 (owner_id=2 和 3 是商家用户)
INSERT INTO store (name, description, address, phone, hours, state, publish_time, review_time, owner_id) VALUES
('张老板的川菜窗口', '正宗川菜，麻辣鲜香，欢迎品尝', '一食堂二楼', '13800001111', '10:00-20:00', 'approved', '2024-10-03 10:00:00', '2024-10-03 11:00:00', 2),
('李师傅的面馆', '手工拉面，汤底浓郁，每日新鲜制作', '二食堂一楼', '13900002222', '09:00-19:00', 'approved', '2024-10-03 12:00:00', '2024-10-03 13:00:00', 3),
('张老板的奶茶铺', '新店开张，多种口味，欢迎品尝', '一食堂一楼', '13800001111', '09:00-21:00', 'pending', '2024-10-04 14:00:00', NULL, 2);

-- 3. 插入餐点信息
-- 川菜窗口的餐点 (store_id=1)
INSERT INTO item (name, description, price, quantity, store_id) VALUES
('宫保鸡丁', '经典川菜，鸡肉鲜嫩，花生香脆，配料：鸡肉、花生、辣椒、花椒', 15.00, 50, 1),
('麻婆豆腐', '麻辣鲜香，豆腐滑嫩，配料：嫩豆腐、牛肉末、豆瓣酱、花椒', 8.00, 40, 1),
('米饭', '东北优质大米，粒粒饱满', 1.00, 200, 1),
('酸辣土豆丝', '酸辣爽口，开胃下饭', 6.00, 30, 1);

-- 面馆的餐点 (store_id=2)
INSERT INTO item (name, description, price, quantity, store_id) VALUES
('红烧牛肉面', '大块牛肉，劲道拉面，汤汁浓郁', 18.00, 60, 2),
('酸菜肉丝面', '酸爽开胃，肉丝鲜嫩', 12.00, 30, 2),
('素面', '清淡健康，配青菜', 8.00, 40, 2),
('加蛋', '新鲜鸡蛋', 2.00, 100, 2);

-- 4. 插入订单 (user_id=4 和 5 是普通用户)
INSERT INTO `order` (user_id, store_id, create_time, review_time, state) VALUES
(4, 1, '2024-10-05 11:00:00', '2024-10-05 11:05:00', 'approved'),
(5, 2, '2024-10-05 12:00:00', NULL, 'pending'),
(4, 2, '2024-10-04 18:00:00', '2024-10-04 18:05:00', 'completed'),
(5, 1, '2024-10-06 09:00:00', '2024-10-06 09:01:00', 'cancelled');

-- 5. 插入订单详情
-- 订单1: 宫保鸡丁套餐 (order_id=1)
INSERT INTO orderitem (order_id, item_id, item_price, quantity) VALUES
(1, 1, 15.00, 1),  -- 宫保鸡丁 x1
(1, 3, 1.00, 2);   -- 米饭 x2

-- 订单2: 红烧牛肉面 (order_id=2)
INSERT INTO orderitem (order_id, item_id, item_price, quantity) VALUES
(2, 5, 18.00, 1);  -- 红烧牛肉面 x1

-- 订单3: 酸菜肉丝面加蛋 (order_id=3)
INSERT INTO orderitem (order_id, item_id, item_price, quantity) VALUES
(3, 6, 12.00, 1),  -- 酸菜肉丝面 x1
(3, 8, 2.00, 1);   -- 加蛋 x1

-- 订单4: 取消的订单 (order_id=4)
INSERT INTO orderitem (order_id, item_id, item_price, quantity) VALUES
(4, 2, 8.00, 1),   -- 麻婆豆腐 x1
(4, 3, 1.00, 1);   -- 米饭 x1

-- 6. 插入评论
INSERT INTO comment (store_id, user_id, content, publish_time, state, review_time) VALUES
(2, 4, '酸菜肉丝面分量足，味道好，性价比高！李师傅手艺不错，推荐！', '2024-10-04 19:00:00', 'approved', '2024-10-04 19:05:00'),
(1, 4, '宫保鸡丁很好吃，就是花生稍微少了点，希望能多放点。', '2024-10-05 13:00:00', 'pending', NULL),
(2, 5, '牛肉面不错，下次还会再来', '2024-10-05 14:00:00', 'approved', '2024-10-05 14:05:00'),
(1, 5, '这家店的菜品都很好吃，值得推荐！', '2024-10-06 10:00:00', 'approved', '2024-10-06 10:05:00');
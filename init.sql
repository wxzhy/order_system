CREATE DATABASE IF NOT EXISTS OrderSystem
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

USE OrderSystem;

-- 1. 用户表 (Users)
-- 基于: User类 , Administrator类 , Vendor类 , Customer类 
CREATE TABLE Users (
    userID INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID ',
    password VARCHAR(255) NOT NULL COMMENT '登录密码 ',
    userType VARCHAR(50) NOT NULL COMMENT '用户类型 (管理员、商家、普通用户) ',
    phone VARCHAR(50) COMMENT '联系电话 ',
    email VARCHAR(100) UNIQUE COMMENT '邮箱地址 ',
    userName VARCHAR(100) COMMENT '用户名称 ',
    createTime DATETIME COMMENT '创建时间 '
);

-- 2. 商家信息表 (Stores)
-- 基于: Store类 
CREATE TABLE Stores (
    storeID INT PRIMARY KEY AUTO_INCREMENT COMMENT '商家ID ',
    userID INT NOT NULL COMMENT '创建用户ID ',
    storeName VARCHAR(255) NOT NULL COMMENT '商家名称 ',
    description TEXT COMMENT '商家简介 ',
    address VARCHAR(255) COMMENT '商家地点 ',
    phone VARCHAR(50) COMMENT '联系电话 ',
    hours VARCHAR(100) COMMENT '营业时间 ',
    imageURL VARCHAR(255) COMMENT '图片文件名 ',
    state VARCHAR(50) COMMENT '审核状态 (待审核、正常营业、已停用) ',
    publishTime DATETIME COMMENT '发布时间 ',
    reviewTime DATETIME COMMENT '审核时间 ',
    FOREIGN KEY (userID) REFERENCES Users(userID)
);

-- 3. 餐点信息表 (Items)
-- 基于: Item类 
CREATE TABLE Items (
    itemID INT PRIMARY KEY AUTO_INCREMENT COMMENT '餐点ID ',
    storeID INT NOT NULL COMMENT '商家ID ',
    itemName VARCHAR(255) NOT NULL COMMENT '餐点名称 ',
    imageURL VARCHAR(255) COMMENT '图片文件名 ',
    description TEXT COMMENT '简介 ',
    price DECIMAL(10, 2) NOT NULL COMMENT '价格 ',
    quantity INT COMMENT '库存数量 ',
    FOREIGN KEY (storeID) REFERENCES Stores(storeID)
);

-- 4. 预约订单表 (Orders)
-- 基于: Order类 
CREATE TABLE Orders (
    orderID INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID ',
    storeID INT NOT NULL COMMENT '商家ID ',
    userID INT NOT NULL COMMENT '用户ID ',
    createTime DATETIME COMMENT '创建时间 ',
    reviewTime DATETIME COMMENT '审核时间 ',
    state VARCHAR(50) COMMENT '审核状态 (待审核，已同意，已完成，已取消) ',
    FOREIGN KEY (storeID) REFERENCES Stores(storeID),
    FOREIGN KEY (userID) REFERENCES Users(userID)
);

-- 5. 订单商品表 (OrderItems)
-- 基于: OrderItem类 
CREATE TABLE OrderItems (
    orderItemID INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单项ID ',
    orderID INT NOT NULL COMMENT '订单ID ',
    itemID INT NOT NULL COMMENT '商品ID ',
    itemPrice DECIMAL(10, 2) COMMENT '单价 ',
    quantity INT NOT NULL COMMENT '数量 ',
    FOREIGN KEY (orderID) REFERENCES Orders(orderID) ON DELETE CASCADE,
    FOREIGN KEY (itemID) REFERENCES Items(itemID)
);

-- 6. 评论表 (Comments)
-- 基于: Comment类 
CREATE TABLE Comments (
    commentID INT PRIMARY KEY AUTO_INCREMENT COMMENT '评论ID ',
    storeID INT NOT NULL COMMENT '商家ID ',
    userID INT NOT NULL COMMENT '评论者ID ',
    content TEXT COMMENT '评论内容 ',
    publishTime DATETIME COMMENT '评论时间 ',
    state VARCHAR(50) COMMENT '审核状态 (未审核，审核通过，审核未通过) ',
    reviewTime DATETIME COMMENT '审核时间 ',
    FOREIGN KEY (storeID) REFERENCES Stores(storeID),
    FOREIGN KEY (userID) REFERENCES Users(userID)
);
-- 插入初始数据
-- 1. 插入用户 (管理员, 商家, 普通用户) 
INSERT INTO Users (password, userType, phone, email, userName, createTime)
VALUES
('admin_pass_hashed', '管理员', '10086', 'admin@nuaa.edu.cn', '系统管理员', '2024-10-01 08:00:00'),
('vendor1_pass_hashed', '商家', '13800001111', 'vendor1@nuaa.edu.cn', '张老板', '2024-10-01 09:00:00'),
('vendor2_pass_hashed', '商家', '13900002222', 'vendor2@nuaa.edu.cn', '李师傅', '2024-10-01 09:30:00'),
('customer1_pass_hashed', '普通用户', '18600003333', 'customer1@nuaa.edu.cn', '小明', '2024-10-02 10:00:00'),
('customer2_pass_hashed', '普通用户', '18600004444', 'customer2@nuaa.edu.cn', '小红', '2024-10-02 11:00:00');

-- 2. 插入商家信息  (userID=2 和 3 是商家)
INSERT INTO Stores (userID, storeName, description, address, phone, hours, state, publishTime, reviewTime)
VALUES
(2, '张老板的川菜窗口', '正宗川菜，麻辣鲜香', '一食堂二楼', '13800001111', '10:00-20:00', '正常营业', '2024-10-03 10:00:00', '2024-10-03 11:00:00'),
(3, '李师傅的面馆', '手工拉面，汤底浓郁', '二食堂一楼', '13900002222', '09:00-19:00', '正常营业', '2024-10-03 12:00:00', '2024-10-03 13:00:00'),
(2, '张老板的奶茶铺', '新店开张，欢迎品尝', '一食堂一楼', '13800001111', '09:00-21:00', '待审核', '2024-10-04 14:00:00', NULL);

-- 3. 插入餐点信息 
-- 川菜窗口 (storeID=1)
INSERT INTO Items (storeID, itemName, description, price, quantity)
VALUES
(1, '宫保鸡丁', '鸡肉、花生、辣椒', 15.00, 50),
(1, '麻婆豆腐', '豆腐、牛肉末、花椒', 8.00, 40),
(1, '米饭', '东北大米', 1.00, 200);
-- 面馆 (storeID=2)
INSERT INTO Items (storeID, itemName, description, price, quantity)
VALUES
(2, '红烧牛肉面', '大块牛肉，劲道拉面', 18.00, 60),
(2, '酸菜肉丝面', '酸爽开胃', 12.00, 30);

-- 4. 插入订单  (userID=4 和 5 是普通用户)
INSERT INTO Orders (storeID, userID, createTime, reviewTime, state)
VALUES
(1, 4, '2024-10-05 11:00:00', '2024-10-05 11:05:00', '已同意'),
(2, 5, '2024-10-05 12:00:00', NULL, '待审核'),
(2, 4, '2024-10-04 18:00:00', '2024-10-04 18:05:00', '已完成'),
(1, 5, '2024-10-06 09:00:00', '2024-10-06 09:01:00', '已取消');

-- 5. 插入订单详情 
-- 订单1 (orderID=1)
INSERT INTO OrderItems (orderID, itemID, itemPrice, quantity)
VALUES
(1, 1, 15.00, 1), -- 宫保鸡丁
(1, 3, 1.00, 2);  -- 米饭
-- 订单2 (orderID=2)
INSERT INTO OrderItems (orderID, itemID, itemPrice, quantity)
VALUES
(2, 4, 18.00, 1); -- 红烧牛肉面
-- 订单3 (orderID=3)
INSERT INTO OrderItems (orderID, itemID, itemPrice, quantity)
VALUES
(3, 5, 12.00, 1); -- 酸菜肉丝面

-- 6. 插入评论 
INSERT INTO Comments (storeID, userID, content, publishTime, state, reviewTime)
VALUES
(2, 4, '酸菜肉丝面分量足，味道好！', '2024-10-04 19:00:00', '审核通过', '2024-10-04 19:05:00'),
(1, 4, '宫保鸡丁好吃，就是花生少了点。', '2024-10-05 13:00:00', '未审核', NULL),
(2, 5, '牛肉面不错', '2024-10-07 12:00:00', '审核未通过', '2024-10-07 12:05:00');
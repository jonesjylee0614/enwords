-- TransLearn 数据库创建脚本
-- MySQL 5.7+

-- 创建数据库
CREATE DATABASE IF NOT EXISTS translearn 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE translearn;

-- 创建用户（可选）
-- CREATE USER 'translearn'@'localhost' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON translearn.* TO 'translearn'@'localhost';
-- FLUSH PRIVILEGES;

-- 提示信息
SELECT 'Database translearn created successfully!' AS message;


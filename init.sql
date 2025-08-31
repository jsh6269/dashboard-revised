-- MySQL 초기화 스크립트

USE `${DB_NAME}`;

-- 전용 사용자 생성 (이미 존재하면 무시)
CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';

-- dashboard_db에 대한 제한된 권한만 부여
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER ON `${DB_NAME}`.* TO '${DB_USER}'@'%';

-- 권한 적용
FLUSH PRIVILEGES;

-- 사용자 생성 확인
SELECT User, Host FROM mysql.user WHERE User IN ('${DB_USER}', 'root');
SHOW GRANTS FOR '${DB_USER}'@'%';

-- 데이터베이스 상태 확인
SHOW DATABASES;
SELECT DATABASE();

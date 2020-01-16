
CREATE TABLE IF NOT EXISTS `config` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `webserver` TEXT,
  `backup_path` TEXT,
  `sites_path` TEXT,
  `status` INTEGER,
  `mysql_root` TEXT
);

INSERT INTO `config` (`id`, `webserver`, `backup_path`, `sites_path`, `status`, `mysql_root`) VALUES
(1, 'nginx', '/opt/slemp/backup', '/opt/slemp/wwwroot', 0, 'admin');


CREATE TABLE IF NOT EXISTS `users` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `username` TEXT,
  `password` TEXT,
  `login_ip` TEXT,
  `login_time` TEXT,
  `phone` TEXT,
  `email` TEXT
);

INSERT INTO `users` (`id`, `username`, `password`, `login_ip`, `login_time`, `phone`, `email`) VALUES
(1, 'admin', '25d55ad283aa400af464c76d713c07ad', '192.168.0.1', '2018-12-10 15:12:56', 0, 'dentix.id@gmail.com');

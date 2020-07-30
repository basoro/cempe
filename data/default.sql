CREATE TABLE "sessions" (
	"session_id" VARCHAR PRIMARY KEY NOT NULL UNIQUE,
	"atime" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"data" TEXT
);

CREATE TABLE IF NOT EXISTS `crontab` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `type` TEXT,
  `where1` TEXT,
  `where_hour` INTEGER,
  `where_minute` INTEGER,
  `echo` TEXT,
  `addtime` TEXT
);

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

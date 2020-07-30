CREATE TABLE `catalogs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `pid` int(11) not null default 0,
  `name` varchar(255) not null default "",
  `url` text,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `products` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `catalog` varchar(255) not null default 0,
  `status` varchar(255) not null default 0,
  `url` varchar(255) not null default 0,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `tags` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) not null default 0,
  `value` varchar(255) not null default 0,
  `updated` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX uniq ON tags(`name`,`value`);
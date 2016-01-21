CREATE DATABASE `testdb` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;

CREATE TABLE `QUESTION` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `NAME` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `LINK_ID` int(10) unsigned NOT NULL,
  `FOCUS` int(10) unsigned NOT NULL,
  `ANSWER` int(10) unsigned NOT NULL,
  `LAST_VISIT` int(10) unsigned DEFAULT NULL,
  `ADD_TIME` int(10) unsigned NOT NULL,
  `TOP_ANSWER_NUMBER` int(10) unsigned NOT NULL,
  `REVIEW` int(10) unsigned NOT NULL,
  `ACTIVATE` int(10) unsigned NOT NULL,
  `FIRST_COMMENT` int(10) unsigned NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `LINK_ID` (`LINK_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=100000 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `TOPIC` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `NAME` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `LAST_VISIT` int(10) unsigned DEFAULT NULL,
  `LINK_ID` int(10) unsigned NOT NULL,
  `ADD_TIME` int(10) unsigned NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `LINK_ID` (`LINK_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


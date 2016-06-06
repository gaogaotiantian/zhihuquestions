use testdb;
CREATE TABLE `USER` (
    `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `NAME` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
    `LINK_ID` varchar(80) NOT NULL,
    `FOLLOWER` int(10) unsigned NOT NULL,
    `FOLLOWEE` int(10) unsigned NOT NULL,
    `ANSWER_NUM` int(10) unsigned NOT NULL,
    `AGREE_NUM` int(10) unsigned NOT NULL,
    `LAST_VISIT` int(10) unsigned NOT NULL,
    PRIMARY KEY (`ID`),
    UNIQUE KEY `LINK_ID` (`LINK_ID`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO `USER` (`ID`, `NAME`, `LINK_ID`, `FOLLOWER`, `FOLLOWEE`, `ANSWER_NUM`, `AGREE_NUM`, `LAST_VISIT`) VALUES (1, 'vczh', 'excited-vczh', 0, 0, 0, 0, 0);

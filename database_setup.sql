CREATE DATABASE  IF NOT EXISTS `ece356_proj`;
USE `ece356_proj`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `Users`
-- ----------------------------
DROP TABLE IF EXISTS `Users`;
CREATE TABLE `Users` (
  `UserID` varchar(255) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `Birthday` date DEFAULT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `Posts`
-- ----------------------------
DROP TABLE IF EXISTS `Posts`;
CREATE TABLE `Posts` (
  `PostID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) DEFAULT NULL,
  `Type` varchar(255) DEFAULT NULL,
  `Content` varchar(255) DEFAULT NULL,
  `CreatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`PostID`),
  FOREIGN KEY (`CreatedBy`) REFERENCES  Users(`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `UserGroups`
-- ----------------------------
DROP TABLE IF EXISTS `UserGroups`;
CREATE TABLE `UserGroups` (
  `GroupID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) DEFAULT NULL,
  `CreatedBy` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`GroupID`),
  FOREIGN KEY (`CreatedBy`) REFERENCES  Users(`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `Topics`
-- ----------------------------
DROP TABLE IF EXISTS `Topics`;
CREATE TABLE `Topics` (
  `TopicID` varchar(255) NOT NULL,
  PRIMARY KEY (`TopicID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `UserFollowsUser`
-- ----------------------------
DROP TABLE IF EXISTS `UserFollowsUser`;
CREATE TABLE `UserFollowsUser` (
  `UserID` varchar(255) NOT NULL,
  `FollowUserID` varchar(255) NOT NULL,
  `LastReadPost` int DEFAULT NULL,
  PRIMARY KEY (`UserID`,`FollowUserID`),
  FOREIGN KEY (`UserID`) REFERENCES  Users(`UserID`),
  FOREIGN KEY (`FollowUserID`) REFERENCES  Users(`UserID`),
  FOREIGN KEY (`LastReadPost`) REFERENCES  Posts(`PostID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `UserFollowsTopic`
-- ----------------------------
DROP TABLE IF EXISTS `UserFollowsTopic`;
CREATE TABLE `UserFollowsTopic` (
  `UserID` varchar(255) NOT NULL,
  `FollowTopicID` varchar(255) NOT NULL,
  `LastReadPost` int DEFAULT NULL,
  PRIMARY KEY (`UserID`,`FollowTopicID`),
  FOREIGN KEY (`UserID`) REFERENCES  Users(`UserID`),
  FOREIGN KEY (`FollowTopicID`) REFERENCES  Topics(`TopicID`),
  FOREIGN KEY (`LastReadPost`) REFERENCES  Posts(`PostID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `UserJoinGroup`
-- ----------------------------
DROP TABLE IF EXISTS `UserJoinGroup`;
CREATE TABLE `UserJoinGroup` (
  `UserID` varchar(255) NOT NULL,
  `GroupID` int NOT NULL,
  PRIMARY KEY (`UserID`,`GroupID`),
  FOREIGN KEY (`UserID`) REFERENCES  Users(`UserID`),
  FOREIGN KEY (`GroupID`) REFERENCES  UserGroups(`GroupID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `PostRespPost`
-- ----------------------------
DROP TABLE IF EXISTS `PostRespPost`;
CREATE TABLE `PostRespPost` (
  `PostID` int NOT NULL,
  `ResponseID` int NOT NULL,
  PRIMARY KEY (`PostID`,`ResponseID`),
  FOREIGN KEY (`PostID`) REFERENCES  Posts(`PostID`),
  FOREIGN KEY (`ResponseID`) REFERENCES  Posts(`PostID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `PostUnderTopic`
-- ----------------------------
DROP TABLE IF EXISTS `PostUnderTopic`;
CREATE TABLE `PostUnderTopic` (
  `PostID` int NOT NULL,
  `TopicID` varchar(255) NOT NULL,
  PRIMARY KEY (`PostID`,`TopicID`),
  FOREIGN KEY (`PostID`) REFERENCES  Posts(`PostID`),
  FOREIGN KEY (`TopicID`) REFERENCES  Topics(`TopicID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



BEGIN;
INSERT INTO `Users` VALUES ('dxy','edward','1997-03-23');
COMMIT;
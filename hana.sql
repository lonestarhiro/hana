-- MySQL dump 10.13  Distrib 8.0.26, for Win64 (x86_64)
--
-- Host: localhost    Database: hana
-- ------------------------------------------------------
-- Server version	8.0.26

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_user'),(22,'Can change user',6,'change_user'),(23,'Can delete user',6,'delete_user'),(24,'Can view user',6,'view_user'),(25,'Can add careuser',7,'add_careuser'),(26,'Can change careuser',7,'change_careuser'),(27,'Can delete careuser',7,'delete_careuser'),(28,'Can view careuser',7,'view_careuser'),(29,'Can add default shift',8,'add_defaultshift'),(30,'Can change default shift',8,'change_defaultshift'),(31,'Can delete default shift',8,'delete_defaultshift'),(32,'Can view default shift',8,'view_defaultshift'),(33,'Can add default schedule',8,'add_defaultschedule'),(34,'Can change default schedule',8,'change_defaultschedule'),(35,'Can delete default schedule',8,'delete_defaultschedule'),(36,'Can view default schedule',8,'view_defaultschedule'),(37,'Can add service',9,'add_service'),(38,'Can change service',9,'change_service'),(39,'Can delete service',9,'delete_service'),(40,'Can view service',9,'view_service'),(41,'Can add schedule',10,'add_schedule'),(42,'Can change schedule',10,'change_schedule'),(43,'Can delete schedule',10,'delete_schedule'),(44,'Can view schedule',10,'view_schedule');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `careusers_careuser`
--

DROP TABLE IF EXISTS `careusers_careuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `careusers_careuser` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `last_name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_kana` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_kana` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` smallint unsigned NOT NULL,
  `birthday` date NOT NULL,
  `user_no` smallint unsigned DEFAULT NULL,
  `postcode` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_ken` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_siku` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_tyou` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_bld` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tel` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `startdate` date NOT NULL,
  `biko` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_no` (`user_no`),
  CONSTRAINT `careusers_careuser_chk_1` CHECK ((`gender` >= 0)),
  CONSTRAINT `careusers_careuser_chk_2` CHECK ((`user_no` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `careusers_careuser`
--

LOCK TABLES `careusers_careuser` WRITE;
/*!40000 ALTER TABLE `careusers_careuser` DISABLE KEYS */;
INSERT INTO `careusers_careuser` VALUES (1,'山田','花子','やまだ','はなこ',1,'1955-07-12',NULL,'5550023','大阪府','大阪市','花川','','0905665456','','2021-08-13','てすとおお',1),(2,'高橋','一子','たかはし','いちこ',1,'1970-09-12',NULL,'555','長野','ながの','ながの','','','','2021-08-13','',1),(3,'鈴木','秀夫','すずき','ひでお',0,'1955-01-12',NULL,'5550023','大阪府','大阪市','あああ','','09086073789','','2021-08-13','',1),(4,'中野','一郎','なかの','いちろう',0,'1955-01-12',NULL,'5550023','大阪','おさか','１','','09086073789','','2021-08-13','',1);
/*!40000 ALTER TABLE `careusers_careuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `careusers_defaultschedule`
--

DROP TABLE IF EXISTS `careusers_defaultschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `careusers_defaultschedule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `type` smallint unsigned NOT NULL,
  `weektype` smallint unsigned NOT NULL,
  `sun` tinyint(1) NOT NULL,
  `mon` tinyint(1) NOT NULL,
  `tue` tinyint(1) NOT NULL,
  `wed` tinyint(1) NOT NULL,
  `thu` tinyint(1) NOT NULL,
  `fri` tinyint(1) NOT NULL,
  `sat` tinyint(1) NOT NULL,
  `daytype` smallint unsigned NOT NULL,
  `day` smallint unsigned DEFAULT NULL,
  `biko` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `careuser_id` bigint NOT NULL,
  `start_h` smallint unsigned DEFAULT NULL,
  `start_m` smallint unsigned DEFAULT NULL,
  `service_id` bigint NOT NULL,
  `peoples` smallint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `careusers_defaultshi_careuser_id_27727f32_fk_careusers` (`careuser_id`),
  KEY `careusers_defaultsch_service_id_0e01e0a7_fk_services_` (`service_id`),
  CONSTRAINT `careusers_defaultsch_service_id_0e01e0a7_fk_services_` FOREIGN KEY (`service_id`) REFERENCES `services_service` (`id`),
  CONSTRAINT `careusers_defaultshi_careuser_id_27727f32_fk_careusers` FOREIGN KEY (`careuser_id`) REFERENCES `careusers_careuser` (`id`),
  CONSTRAINT `careusers_defaultschedule_chk_1` CHECK ((`type` >= 0)),
  CONSTRAINT `careusers_defaultschedule_chk_2` CHECK ((`weektype` >= 0)),
  CONSTRAINT `careusers_defaultschedule_chk_3` CHECK ((`daytype` >= 0)),
  CONSTRAINT `careusers_defaultschedule_chk_4` CHECK ((`day` >= 0)),
  CONSTRAINT `careusers_defaultschedule_chk_5` CHECK ((`start_h` >= 0)),
  CONSTRAINT `careusers_defaultschedule_chk_6` CHECK ((`start_m` >= 0)),
  CONSTRAINT `careusers_defaultschedule_chk_7` CHECK ((`peoples` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `careusers_defaultschedule`
--

LOCK TABLES `careusers_defaultschedule` WRITE;
/*!40000 ALTER TABLE `careusers_defaultschedule` DISABLE KEYS */;
INSERT INTO `careusers_defaultschedule` VALUES (2,1,0,0,0,0,0,0,0,0,3,10,'',1,12,0,2,2),(3,0,0,0,0,1,0,1,0,0,0,NULL,'',1,7,0,4,1),(5,0,0,1,0,0,0,1,0,0,0,NULL,'',2,11,0,2,1),(13,1,0,0,0,0,0,0,0,0,0,NULL,'',4,15,0,31,1),(15,0,0,0,0,0,1,1,0,0,0,NULL,'',2,12,0,5,1),(45,0,0,1,1,1,1,1,1,1,0,NULL,'',4,9,0,3,1),(47,1,0,0,0,0,0,0,0,0,0,NULL,'備考テスト',4,19,0,1,1);
/*!40000 ALTER TABLE `careusers_defaultschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `careusers_defaultschedule_staffs`
--

DROP TABLE IF EXISTS `careusers_defaultschedule_staffs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `careusers_defaultschedule_staffs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `defaultschedule_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `careusers_defaultschedul_defaultschedule_id_user__63ffc61b_uniq` (`defaultschedule_id`,`user_id`),
  KEY `careusers_defaultsch_user_id_2b269ae2_fk_staffs_us` (`user_id`),
  CONSTRAINT `careusers_defaultsch_defaultschedule_id_9fc4125a_fk_careusers` FOREIGN KEY (`defaultschedule_id`) REFERENCES `careusers_defaultschedule` (`id`),
  CONSTRAINT `careusers_defaultsch_user_id_2b269ae2_fk_staffs_us` FOREIGN KEY (`user_id`) REFERENCES `staffs_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `careusers_defaultschedule_staffs`
--

LOCK TABLES `careusers_defaultschedule_staffs` WRITE;
/*!40000 ALTER TABLE `careusers_defaultschedule_staffs` DISABLE KEYS */;
INSERT INTO `careusers_defaultschedule_staffs` VALUES (9,3,3),(11,13,2);
/*!40000 ALTER TABLE `careusers_defaultschedule_staffs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_staffs_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_staffs_user_id` FOREIGN KEY (`user_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2021-08-14 04:25:14.140583','1','DefaultSchedule object (1)',1,'[{\"added\": {}}]',8,1),(2,'2021-08-14 07:07:29.112137','2','DefaultSchedule object (2)',1,'[{\"added\": {}}]',8,1),(3,'2021-08-14 09:08:24.990402','1','山田 花子',2,'[{\"changed\": {\"fields\": [\"\\u65e5\"]}}]',8,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(7,'careusers','careuser'),(8,'careusers','defaultschedule'),(4,'contenttypes','contenttype'),(10,'schedules','schedule'),(9,'services','service'),(5,'sessions','session'),(6,'staffs','user');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2021-08-13 11:52:28.395367'),(2,'contenttypes','0002_remove_content_type_name','2021-08-13 11:52:28.499719'),(3,'auth','0001_initial','2021-08-13 11:52:28.846514'),(4,'auth','0002_alter_permission_name_max_length','2021-08-13 11:52:28.912315'),(5,'auth','0003_alter_user_email_max_length','2021-08-13 11:52:28.920153'),(6,'auth','0004_alter_user_username_opts','2021-08-13 11:52:28.926109'),(7,'auth','0005_alter_user_last_login_null','2021-08-13 11:52:28.931889'),(8,'auth','0006_require_contenttypes_0002','2021-08-13 11:52:28.934881'),(9,'auth','0007_alter_validators_add_error_messages','2021-08-13 11:52:28.940866'),(10,'auth','0008_alter_user_username_max_length','2021-08-13 11:52:28.946850'),(11,'auth','0009_alter_user_last_name_max_length','2021-08-13 11:52:28.953157'),(12,'auth','0010_alter_group_name_max_length','2021-08-13 11:52:28.966151'),(13,'auth','0011_update_proxy_permissions','2021-08-13 11:52:28.972135'),(14,'auth','0012_alter_user_first_name_max_length','2021-08-13 11:52:28.995620'),(15,'staffs','0001_initial','2021-08-13 11:52:29.465579'),(16,'admin','0001_initial','2021-08-13 11:52:29.772265'),(17,'admin','0002_logentry_remove_auto_add','2021-08-13 11:52:29.780727'),(18,'admin','0003_logentry_add_action_flag_choices','2021-08-13 11:52:29.788728'),(19,'careusers','0001_initial','2021-08-13 11:52:29.823878'),(20,'sessions','0001_initial','2021-08-13 11:52:29.861452'),(21,'careusers','0002_defaultshift','2021-08-13 12:38:26.430601'),(22,'careusers','0003_rename_defaultshift_defaultschedule','2021-08-13 12:42:47.020320'),(23,'careusers','0002_alter_careuser_adr_ken','2021-08-14 03:34:07.661736'),(24,'staffs','0002_alter_user_adr_ken','2021-08-14 03:34:07.672697'),(25,'careusers','0003_auto_20210814_1900','2021-08-14 10:00:52.481824'),(26,'careusers','0004_alter_defaultschedule_staffs','2021-08-18 12:12:47.402161'),(27,'staffs','0003_user_short_name','2021-08-18 12:12:47.473237'),(28,'careusers','0005_auto_20210819_1444','2021-08-19 05:44:43.529725'),(29,'services','0001_initial','2021-08-19 05:44:43.562874'),(30,'services','0002_alter_service_kind','2021-08-19 06:24:15.093293'),(31,'careusers','0006_defaultschedule_service','2021-08-19 06:24:15.195462'),(32,'schedules','0001_initial','2021-08-20 09:33:19.843878'),(33,'schedules','0002_auto_20210820_1830','2021-08-20 09:33:20.672147'),(34,'schedules','0003_auto_20210820_1833','2021-08-20 09:33:22.811643'),(35,'schedules','0004_auto_20210820_1905','2021-08-20 10:06:00.801739'),(36,'schedules','0005_auto_20210820_1906','2021-08-20 10:06:47.588918'),(37,'schedules','0006_auto_20210820_1908','2021-08-20 10:08:47.386462'),(38,'schedules','0007_schedule_from_default','2021-08-20 10:54:06.913866'),(39,'schedules','0008_auto_20210821_0010','2021-08-20 15:10:07.565011'),(40,'careusers','0007_auto_20210826_1527','2021-08-26 06:27:39.781307'),(41,'schedules','0009_schedule_peoples','2021-08-26 06:27:39.902384'),(42,'services','0003_alter_service_kind','2021-08-26 06:27:39.910743'),(43,'staffs','0004_auto_20210826_1527','2021-08-26 06:27:39.936477'),(44,'careusers','0008_auto_20210826_1606','2021-08-26 07:06:16.027646'),(45,'schedules','0010_auto_20210826_1615','2021-08-26 07:15:58.807155'),(46,'schedules','0011_auto_20210827_0033','2021-08-26 15:33:58.079111');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('s45ms7yhndzdu4hmturi94nsjr5ia9g6','.eJxVjEEOwiAQRe_C2pACM0BduvcMZJghUjU0Ke3KeHdt0oVu_3vvv1Siba1p62VJk6izMur0u2XiR2k7kDu126x5busyZb0r-qBdX2cpz8vh_h1U6vVbjz7GQQwaHHzg4PwIEB1LKGBzZuvIBBRr0RsCBoxkWRAgYHbZEqn3B6oqNtY:1mHW9b:8jj1tswT1DnY8jpjz5gXRTtxkR7aDx9NRR8jV6xqn7g','2021-09-04 18:55:39.245220');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedules_schedule`
--

DROP TABLE IF EXISTS `schedules_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedules_schedule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `start_date` datetime(6) NOT NULL,
  `biko` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `kaigo_point` smallint unsigned NOT NULL,
  `shogai_point` smallint unsigned NOT NULL,
  `careuser_id` bigint NOT NULL,
  `service_id` bigint NOT NULL,
  `staff1_id` bigint DEFAULT NULL,
  `staff2_id` bigint DEFAULT NULL,
  `staff3_id` bigint DEFAULT NULL,
  `staff4_id` bigint DEFAULT NULL,
  `tr_staff1_id` bigint DEFAULT NULL,
  `tr_staff2_id` bigint DEFAULT NULL,
  `tr_staff3_id` bigint DEFAULT NULL,
  `tr_staff4_id` bigint DEFAULT NULL,
  `from_default` tinyint(1) NOT NULL,
  `peoples` smallint unsigned NOT NULL,
  `check_flg` tinyint(1) NOT NULL,
  `comfirm_flg` tinyint(1) NOT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `schedules_schedule_careuser_id_8707125f_fk_careusers_careuser_id` (`careuser_id`),
  KEY `schedules_schedule_service_id_fc9357ea_fk_services_service_id` (`service_id`),
  KEY `schedules_schedule_tr_staff1_id_751c7342_fk_staffs_user_id` (`tr_staff1_id`),
  KEY `schedules_schedule_tr_staff2_id_2487da56_fk_staffs_user_id` (`tr_staff2_id`),
  KEY `schedules_schedule_tr_staff3_id_7a457006_fk_staffs_user_id` (`tr_staff3_id`),
  KEY `schedules_schedule_tr_staff4_id_5ca474df_fk_staffs_user_id` (`tr_staff4_id`),
  KEY `schedules_schedule_staff1_id_5f5bcb60_fk_staffs_user_id` (`staff1_id`),
  KEY `schedules_schedule_staff2_id_fcc4a5cb_fk_staffs_user_id` (`staff2_id`),
  KEY `schedules_schedule_staff3_id_961acd55_fk_staffs_user_id` (`staff3_id`),
  KEY `schedules_schedule_staff4_id_ec0e8357_fk_staffs_user_id` (`staff4_id`),
  CONSTRAINT `schedules_schedule_careuser_id_8707125f_fk_careusers_careuser_id` FOREIGN KEY (`careuser_id`) REFERENCES `careusers_careuser` (`id`),
  CONSTRAINT `schedules_schedule_service_id_fc9357ea_fk_services_service_id` FOREIGN KEY (`service_id`) REFERENCES `services_service` (`id`),
  CONSTRAINT `schedules_schedule_staff1_id_5f5bcb60_fk_staffs_user_id` FOREIGN KEY (`staff1_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_staff2_id_fcc4a5cb_fk_staffs_user_id` FOREIGN KEY (`staff2_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_staff3_id_961acd55_fk_staffs_user_id` FOREIGN KEY (`staff3_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_staff4_id_ec0e8357_fk_staffs_user_id` FOREIGN KEY (`staff4_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_tr_staff1_id_751c7342_fk_staffs_user_id` FOREIGN KEY (`tr_staff1_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_tr_staff2_id_2487da56_fk_staffs_user_id` FOREIGN KEY (`tr_staff2_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_tr_staff3_id_7a457006_fk_staffs_user_id` FOREIGN KEY (`tr_staff3_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_tr_staff4_id_5ca474df_fk_staffs_user_id` FOREIGN KEY (`tr_staff4_id`) REFERENCES `staffs_user` (`id`),
  CONSTRAINT `schedules_schedule_chk_1` CHECK ((`kaigo_point` >= 0)),
  CONSTRAINT `schedules_schedule_chk_2` CHECK ((`shogai_point` >= 0)),
  CONSTRAINT `schedules_schedule_chk_3` CHECK ((`peoples` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedules_schedule`
--

LOCK TABLES `schedules_schedule` WRITE;
/*!40000 ALTER TABLE `schedules_schedule` DISABLE KEYS */;
INSERT INTO `schedules_schedule` VALUES (1,'2021-08-19 00:00:00.000000','',0,0,1,2,2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-08-19 00:30:00.000000'),(2,'2021-08-25 02:00:00.000000','',0,0,2,3,1,2,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-08-25 03:00:00.000000'),(3,'2021-08-21 01:00:00.000000','',0,0,3,5,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-08-21 02:00:00.000000'),(4,'2021-08-27 07:00:00.000000','',0,0,1,1,2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-08-27 07:30:00.000000'),(5,'2021-08-30 03:00:00.000000','',0,0,3,1,3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-08-30 03:30:00.000000'),(6,'2021-08-18 17:00:00.000000','',0,0,1,3,2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-08-18 18:00:00.000000'),(7,'2021-09-19 06:00:00.000000','テスト',23,43,1,2,1,2,3,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-19 06:30:00.000000'),(8,'2021-09-05 00:30:00.000000','',0,0,2,6,2,1,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-05 02:00:00.000000'),(9,'2021-09-05 03:00:00.000000','',0,0,2,5,2,1,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-05 04:00:00.000000'),(10,'2021-09-05 05:00:00.000000','',0,0,2,1,2,1,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-05 05:30:00.000000'),(11,'2021-09-05 07:00:00.000000','',0,0,2,5,2,1,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-05 08:00:00.000000'),(12,'2021-09-05 09:00:00.000000','',0,0,2,2,2,1,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-05 09:30:00.000000'),(13,'2021-09-05 12:00:00.000000','',0,0,2,10,2,1,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-05 13:30:00.000000'),(14,'2021-09-06 05:00:00.000000','',0,0,2,6,3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,1,0,0,'2021-09-06 06:30:00.000000');
/*!40000 ALTER TABLE `schedules_schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services_service`
--

DROP TABLE IF EXISTS `services_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `services_service` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `kind` smallint unsigned NOT NULL,
  `title` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `time` smallint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `services_service_chk_1` CHECK ((`kind` >= 0)),
  CONSTRAINT `services_service_chk_2` CHECK ((`time` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services_service`
--

LOCK TABLES `services_service` WRITE;
/*!40000 ALTER TABLE `services_service` DISABLE KEYS */;
INSERT INTO `services_service` VALUES (1,0,'身体30',30),(2,0,'生活30',30),(3,0,'身体60',60),(4,0,'生活60',60),(5,0,'身体30/生活30',60),(6,0,'身体90',90),(7,0,'生活90',90),(8,0,'身体60/生活30',90),(9,0,'身体30/生活60',90),(10,0,'同行援護90',90),(11,1,'身体30',30),(12,1,'生活30',30),(13,1,'身体60',60),(14,1,'家事60',60),(15,1,'身体30/家事30',60),(16,1,'身体90',90),(17,1,'家事90',90),(18,1,'身体60/家事30',90),(19,1,'身体30/家事60',90),(20,1,'重度障害30',30),(21,1,'重度障害60',60),(22,1,'重度障害90',90),(23,1,'重度障害120',120),(24,1,'通院30',30),(25,1,'通院60',60),(26,1,'通院90',90),(27,1,'通院120',120),(28,1,'通院150',150),(29,1,'通院180',180),(30,2,'移動支援30',30),(31,2,'移動支援60',60),(32,2,'移動支援90',90),(33,2,'移動支援120',120),(34,2,'移動支援150',150),(35,2,'移動支援180',180);
/*!40000 ALTER TABLE `services_service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staffs_user`
--

DROP TABLE IF EXISTS `staffs_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staffs_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `last_kana` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_kana` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `birthday` date DEFAULT NULL,
  `staff_no` smallint unsigned DEFAULT NULL,
  `postcode` varchar(7) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_ken` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_siku` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_tyou` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `adr_bld` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tel` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shaho` tinyint(1) NOT NULL,
  `join` date DEFAULT NULL,
  `biko` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `kanri` tinyint(1) NOT NULL,
  `jimu` tinyint(1) NOT NULL,
  `reader` tinyint(1) NOT NULL,
  `caremane` tinyint(1) NOT NULL,
  `servkan` tinyint(1) NOT NULL,
  `kaigo` tinyint(1) NOT NULL,
  `yougu` tinyint(1) NOT NULL,
  `kango` tinyint(1) NOT NULL,
  `kinou` tinyint(1) NOT NULL,
  `seikatu` tinyint(1) NOT NULL,
  `ishi` tinyint(1) NOT NULL,
  `riha` tinyint(1) NOT NULL,
  `ope` tinyint(1) NOT NULL,
  `ryouyou` tinyint(1) NOT NULL,
  `jihakan` tinyint(1) NOT NULL,
  `sidou` tinyint(1) NOT NULL,
  `hoiku` tinyint(1) NOT NULL,
  `jisou` tinyint(1) NOT NULL,
  `driver` tinyint(1) NOT NULL,
  `eiyou` tinyint(1) NOT NULL,
  `tyouri` tinyint(1) NOT NULL,
  `gengo` tinyint(1) NOT NULL,
  `tyounou` tinyint(1) NOT NULL,
  `short_name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `staff_no` (`staff_no`),
  CONSTRAINT `staffs_user_chk_1` CHECK ((`staff_no` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staffs_user`
--

LOCK TABLES `staffs_user` WRITE;
/*!40000 ALTER TABLE `staffs_user` DISABLE KEYS */;
INSERT INTO `staffs_user` VALUES (1,'2021-08-21 18:55:39.241168',1,'hirotoka@hotmail.com','山田','太郎','pbkdf2_sha256$260000$C9Ef1pJFGB0EBLHJouHABr$A5ZXpkRq09Zgj5t1Mnor62NdfY+rHgfbrlwJ2tDAfFM=',1,1,'2021-08-13 11:53:16.196728','かすが','ひろと','1976-09-24',NULL,'555','大阪府','大阪市','1','','09052454545','',0,'2021-08-11','',1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''),(2,NULL,0,'nagaisi@be-r.jp','池田','花子','pbkdf2_sha256$260000$ycfczlGKKomD8OAegE0IZR$zTcClO6MSvjnzAe0FuYfCpFr2F9KmCOIsjUv9QX0QjY=',1,1,'2021-08-14 11:42:56.863890','たかはし','はなこ','1976-06-18',NULL,'555','大阪府','大阪市西淀川区','はな','','','',0,'2021-08-11','',1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,''),(3,NULL,0,'samurai@be-r.jp','侍','三郎','pbkdf2_sha256$260000$NVQPipjvrW3yJrz1LWnRHf$RpZMICI7wxIpD8GHFQmoOwg0tkBCJhkEhiUacfkM1ak=',0,1,'2021-08-18 04:36:08.612346','さむらい','さぶろう','1956-05-12',NULL,'551','大阪府','大阪市','126','','','',0,'2021-08-10','',0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'侍(三)');
/*!40000 ALTER TABLE `staffs_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staffs_user_groups`
--

DROP TABLE IF EXISTS `staffs_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staffs_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `staffs_user_groups_user_id_group_id_58498803_uniq` (`user_id`,`group_id`),
  KEY `staffs_user_groups_group_id_a11c1728_fk_auth_group_id` (`group_id`),
  CONSTRAINT `staffs_user_groups_group_id_a11c1728_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `staffs_user_groups_user_id_9f22fac1_fk_staffs_user_id` FOREIGN KEY (`user_id`) REFERENCES `staffs_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staffs_user_groups`
--

LOCK TABLES `staffs_user_groups` WRITE;
/*!40000 ALTER TABLE `staffs_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `staffs_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staffs_user_user_permissions`
--

DROP TABLE IF EXISTS `staffs_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staffs_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `staffs_user_user_permissions_user_id_permission_id_7da12155_uniq` (`user_id`,`permission_id`),
  KEY `staffs_user_user_per_permission_id_6892ff15_fk_auth_perm` (`permission_id`),
  CONSTRAINT `staffs_user_user_per_permission_id_6892ff15_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `staffs_user_user_permissions_user_id_d3b880bd_fk_staffs_user_id` FOREIGN KEY (`user_id`) REFERENCES `staffs_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staffs_user_user_permissions`
--

LOCK TABLES `staffs_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `staffs_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `staffs_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-08-27 18:06:05

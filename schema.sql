-- MySQL dump 10.13  Distrib 8.4.13, for Linux (aarch64)
--
-- Host: localhost    Database: overwatch_telemetry
-- ------------------------------------------------------
-- Server version	8.4.13-0ubuntu0.26.04.2

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
-- Table structure for table `match_logs`
--

DROP TABLE IF EXISTS `match_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `match_logs` (
  `match_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int DEFAULT NULL,
  `logged_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `result` enum('WIN','LOSS','DRAW','PENDING') DEFAULT 'PENDING',
  `role_played` enum('TANK','DAMAGE','SUPPORT') DEFAULT NULL,
  `hero_name` varchar(50) DEFAULT NULL,
  `connection_feel` enum('SMOOTH','MINOR_LAG','UNPLAYABLE') DEFAULT NULL,
  `notes` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`match_id`),
  UNIQUE KEY `session_id` (`session_id`),
  CONSTRAINT `match_logs_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `match_sessions` (`session_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `match_sessions`
--

DROP TABLE IF EXISTS `match_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `match_sessions` (
  `session_id` int NOT NULL AUTO_INCREMENT,
  `started_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ended_at` timestamp NULL DEFAULT NULL,
  `duration_sec` int DEFAULT NULL,
  `server_ip` varchar(45) DEFAULT NULL,
  `pcap_filename` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`session_id`),
  KEY `idx_started_at` (`started_at`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `network_snapshots`
--

DROP TABLE IF EXISTS `network_snapshots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_snapshots` (
  `snapshot_id` int NOT NULL AUTO_INCREMENT,
  `session_id` int DEFAULT NULL,
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `target_region` varchar(32) NOT NULL,
  `avg_ping_ms` decimal(6,2) NOT NULL,
  `min_ping_ms` decimal(6,2) NOT NULL,
  `max_ping_ms` decimal(6,2) NOT NULL,
  `jitter_ms` decimal(6,2) NOT NULL,
  `packet_loss_pct` decimal(5,2) NOT NULL,
  `dns_lookup_ms` decimal(6,2) NOT NULL,
  `worst_hop_ip` varchar(45) DEFAULT NULL,
  `worst_hop_loss_pct` decimal(5,2) DEFAULT '0.00',
  `alert_triggered` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`snapshot_id`),
  KEY `idx_recorded_at` (`recorded_at`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `network_snapshots_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `match_sessions` (`session_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=238 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-26  2:30:09

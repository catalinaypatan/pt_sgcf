-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 11-11-2025 a las 15:40:50
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `tt`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `correos_actuales`
--

CREATE TABLE `correos_actuales` (
  `id` int(11) NOT NULL,
  `correo` varchar(255) NOT NULL,
  `match_code_empresa` varchar(255) NOT NULL,
  `nombre_lista` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `correos_actuales`
--

INSERT INTO `correos_actuales` (`id`, `correo`, `match_code_empresa`, `nombre_lista`) VALUES
(1, 'ejemplo@docu.cl', 'HAPAG01', 'Docu'),
(3, 'ejemplo@CopyOfBL.cl', 'HAPAG01', 'Copy of BL'),
(4, 'ejemplo@arrivalnotice.cl', 'HAPAG01', 'Arrival Notice');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitudes`
--

CREATE TABLE `solicitudes` (
  `id` int(11) NOT NULL,
  `fecha_solicitud` datetime NOT NULL DEFAULT current_timestamp(),
  `correo_solicitante` varchar(255) NOT NULL,
  `tipo_solicitud` varchar(255) NOT NULL COMMENT 'Creación / Eliminación',
  `correo` varchar(255) NOT NULL,
  `match_code_empresa` varchar(255) NOT NULL,
  `nombre_lista` varchar(255) NOT NULL,
  `estado_solicitud` varchar(255) NOT NULL COMMENT 'pendiente/procesada/anulada',
  `anulada_por` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `correo` varchar(255) NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `apellido` varchar(255) NOT NULL,
  `empresa` varchar(255) NOT NULL,
  `match_code_empresa` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`correo`, `nombre`, `apellido`, `empresa`, `match_code_empresa`) VALUES
('catalinaypatan@gmail.com', 'Catalina', 'Vidal', 'Hapag Lloyd', 'HAPAG01');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `correos_actuales`
--
ALTER TABLE `correos_actuales`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `correos_actuales`
--
ALTER TABLE `correos_actuales`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=85;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

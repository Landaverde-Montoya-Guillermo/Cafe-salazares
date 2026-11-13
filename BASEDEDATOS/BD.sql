-- Active: 1794535651012@@127.0.0.1@3306@bd_coffeelytics
 USE bd_coffeElytics 

 CREATE TABLE proveedor(
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    dirCalle VARCHAR(30) NOT NULL,
    dirColonia VARCHAR(30) NOT NULL,
    dirNumero VARCHAR(12) NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    ciudad VARCHAR(20) NOT NULL,
    PRIMARY KEY (codigo)
 )

 CREATE TABLE tipo_merma(
    codigo VARCHAR(5) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    PRIMARY KEY (codigo),
    UNIQUE(nombre)
 )

 CREATE TABLE estante(
    codigo INT NOT NULL AUTO_INCREMENT ,
    capacidad INT NOT NULL,
    secciones INT NOT NULL,
    PRIMARY KEY (codigo)
 )

 CREATE TABLE estatus(
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR (15) NOT NULL,
    descripcion VARCHAR(50) NOT NULL,
    PRIMARY KEY(codigo)
 )
 
 CREATE TABLE categoria_insumo(
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY(codigo)
 )

 CREATE TABLE ESTATUS_PRODUCTO(
    codigo INT  AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(20) NOT NULL,
    PRIMARY KEY(codigo),
    UNIQUE(nombre)
 )

 CREATE TABLE producto(
    codigo varchar(4) NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    estatus INT NOT NULL,
    PRIMARY KEY(codigo),
    UNIQUE(nombre),
    Foreign Key (estatus) REFERENCES ESTATUS_PRODUCTO(codigo)
 )

 CREATE TABLE unidad_medida(
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    abreviatura VARCHAR(8) NOT NULL,
    PRIMARY KEY(codigo),
    UNIQUE(nombre)
 )

 CREATE TABLE rol(
    codigo VARCHAR(4) NOT NULL,
    nombre VARCHAR(15) NOT NULL,
    PRIMARY KEY(codigo),
    UNIQUE(nombre)
 )

 CREATE TABLE metodo_pago(
    codigo VARCHAR(4) NOT NULL,
    descripcion VARCHAR(30) NOT NULL,
    PRIMARY KEY(codigo),
    UNIQUE(descripcion)
 )

 CREATE TABLE receta(
    codigo VARCHAR(4) NOT NULL,
    producto VARCHAR(4) NOT NULL,
    PRIMARY KEY(codigo),
    Foreign Key (producto) REFERENCES producto(codigo)
 )
 
 CREATE TABLE empleado(
    num INT AUTO_INCREMENT,
    nombrePila VARCHAR(30) NOT NULL,
    primApell VARCHAR(30) NOT NULL,
    segApell VARCHAR(30),
    RFC VARCHAR(12) NOT NULL,
    telefono VARCHAR(10),
    rol VARCHAR(4) NOT NULL,
    PRIMARY KEY(num),
    UNIQUE(RFC),
    Foreign Key (rol) REFERENCES rol(codigo)
 )

 CREATE TABLE compra(
    codigo INT AUTO_INCREMENT,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    proveedor VARCHAR(4) NOT NULL,
    metodoPago VARCHAR(4) NOT NULL,
    empleado INT NOT NULL,
    PRIMARY KEY(codigo),
    Foreign Key (proveedor) REFERENCES proveedor(codigo),
    Foreign Key (metodoPago) REFERENCES metodo_pago(codigo),
    Foreign Key (empleado) REFERENCES empleado(num)
 )

 CREATE TABLE venta(
    codigo INT AUTO_INCREMENT,
    fecha DATE NOT NULL,
    total DECIMAL(10,2) NOT NULL, 
    metodoPago VARCHAR(4) NOT NULL,
    empleado INT NOT NULL,
    PRIMARY KEY(codigo),
    Foreign Key (metodoPago) REFERENCES metodo_pago(codigo),
    Foreign Key (empleado) REFERENCES empleado(num)
 )

 CREATE TABLE insumo(
    codigo VARCHAR(6) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    stockActual DECIMAL(10,2) NOT NULL DEFAULT 0,
    stockMin DECIMAL(10,2) NOT NULL DEFAULT 0,
    seccion TINYINT not null,
    unidad VARCHAR(4) not null,
    estante int not null,
    categoria VARCHAR(4) not null,
    PRIMARY KEY(codigo),
    UNIQUE(nombre),
    Foreign Key (estante) REFERENCES estante(codigo),
    Foreign Key (unidad) REFERENCES unidad_medida(codigo),
    Foreign Key (categoria) REFERENCES categoria_insumo(codigo)
 )

 CREATE TABLE consumible_mesa(
    codigo VARCHAR(5) NOT NULL,
    nombre VARCHAR(40) NOT NULL,
    empleado INT NOT NULL,
    PRIMARY KEY(codigo),
    UNIQUE(nombre),
    Foreign Key (empleado) REFERENCES empleado(num)
 )

 CREATE TABLE factura(
    codigo VARCHAR(8) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    folioFiscal VARCHAR(36) NOT NULL,
    fecha DATE NOT NULL,
    compra INT NOT NULL,
    PRIMARY KEY(codigo),
    UNIQUE(folioFiscal),
    Foreign Key (compra) REFERENCES compra(codigo)
 )

 CREATE TABLE merma(
    codigo INT NOT NULL AUTO_INCREMENT,
    motivo VARCHAR(300) NOT NULL,
    fecha DATE NOT NULL,
    cantidad DECIMAL NOT NULL,
    tipo VARCHAR(5) NOT NULL,
    insumo VARCHAR(6) NOT NULL,
    PRIMARY KEY(codigo),
    Foreign Key (tipo) REFERENCES tipo_merma(codigo),
    Foreign Key (insumo) REFERENCES insumo(codigo)
 )

 CREATE TABLE prod_venta(
    venta INT NOT NULL,
    producto VARCHAR(4) NOT NULL,
    cantidad INT NOT NULL,
    precioUnitarioVenta DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    totalIVA DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    PRIMARY KEY(venta, producto),
    Foreign Key (venta) REFERENCES venta(codigo),
    Foreign Key (producto) REFERENCES producto(codigo)
 )

 CREATE TABLE con_insum(
    insumo VARCHAR(6) NOT NULL,
    mesa VARCHAR(5) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    PRIMARY KEY(insumo, mesa),
    Foreign Key (insumo) REFERENCES insumo(codigo),
    Foreign Key (mesa) REFERENCES consumible_mesa(codigo)
 )

 CREATE TABLE insum_com(
    compra INT NOT NULL,
    insumo VARCHAR(6) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    precioUnitarioVenta DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    totalIVA DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    PRIMARY KEY(compra, insumo),
    Foreign Key (compra) REFERENCES compra(codigo),
    Foreign Key (insumo) REFERENCES insumo(codigo)
 )

 CREATE TABLE rec_insum(
    insumo VARCHAR(6) NOT NULL,
    receta VARCHAR(4) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    PRIMARY KEY(insumo, receta),
    Foreign Key (insumo) REFERENCES insumo(codigo),
    Foreign Key (receta) REFERENCES receta(codigo)
 )
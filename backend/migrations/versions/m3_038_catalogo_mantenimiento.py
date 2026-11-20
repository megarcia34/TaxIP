"""m3_038: catalogo maestro de mantenimiento + encargado + config

Revision ID: m3_038
Revises: m3_037

Responsabilidad unica: crear el catalogo global (sistemas, subsistemas,
componentes, controles), el checklist de inspeccion diaria, y las tablas
por tenant (encargado, configuracion del vehiculo, configuracion del tenant).

NO crea tablas de planes ni de OT (eso va en m3_039 y R26+).
NO toca datos existentes.

Seed:
- 15 sistemas
- 61 subsistemas
- ~102 componentes (sin duplicados entre sistemas)
- 7 controles genericos
- 16 items de checklist de inspeccion
- 0 encargados, 0 configs (se llenan on-demand)

Baseline: m3_037 (head).
"""
from alembic import op

revision = 'm3_038'
down_revision = 'm3_037'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1. TABLAS DE CATALOGO GLOBAL
    # ============================================================

    # 1.1. Sistemas
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_catalogo_sistema (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre varchar(100) NOT NULL UNIQUE,
            descripcion text,
            orden int NOT NULL DEFAULT 0,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now()
        );
    """)

    # 1.2. Subsistemas
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_catalogo_subsistema (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            sistema_id uuid NOT NULL
                REFERENCES mantenimiento_catalogo_sistema(id) ON DELETE CASCADE,
            nombre varchar(100) NOT NULL,
            descripcion text,
            orden int NOT NULL DEFAULT 0,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now(),
            UNIQUE (sistema_id, nombre)
        );
    """)

    # 1.3. Componentes
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_catalogo_componente (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            subsistema_id uuid NOT NULL
                REFERENCES mantenimiento_catalogo_subsistema(id) ON DELETE CASCADE,
            nombre varchar(100) NOT NULL,
            descripcion text,
            orden int NOT NULL DEFAULT 0,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now(),
            UNIQUE (subsistema_id, nombre)
        );
    """)

    # 1.4. Controles (7 genericos con componente_id = NULL)
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_catalogo_control (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            componente_id uuid
                REFERENCES mantenimiento_catalogo_componente(id) ON DELETE CASCADE,
            nombre varchar(100) NOT NULL,
            tipo varchar(20) NOT NULL
                CHECK (tipo IN ('visual', 'instrumental', 'documental')),
            unidad varchar(20),
            rango_normal varchar(50),
            orden int NOT NULL DEFAULT 0,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now()
        );
    """)

    # 1.5. Compatibilidad (sin seed inicial)
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_catalogo_componente_compatibilidad (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            componente_id uuid NOT NULL
                REFERENCES mantenimiento_catalogo_componente(id) ON DELETE CASCADE,
            marca varchar(100),
            modelo varchar(100),
            anio_desde int,
            anio_hasta int,
            motorizacion varchar(20),
            created_at timestamp NOT NULL DEFAULT now()
        );
    """)

    # 1.6. Checklist de inspeccion diaria
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_checklist_inspeccion (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre varchar(100) NOT NULL UNIQUE,
            descripcion text,
            tipo_inspeccion varchar(20) NOT NULL
                CHECK (tipo_inspeccion IN ('inicio', 'fin', 'ambos')),
            componente_id uuid
                REFERENCES mantenimiento_catalogo_componente(id) ON DELETE SET NULL,
            tipo_respuesta varchar(20) NOT NULL
                CHECK (tipo_respuesta IN ('ok_novedad', 'nivel', 'estado_visual', 'si_no', 'texto_libre')),
            opciones jsonb,
            severidad_default varchar(20)
                CHECK (severidad_default IN ('baja', 'media', 'alta', 'critica')),
            orden int NOT NULL DEFAULT 0,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now()
        );
    """)

    # ============================================================
    # 2. TABLAS POR TENANT
    # ============================================================

    # 2.1. Encargado
    op.execute("""
        CREATE TABLE IF NOT EXISTS fleet.encargado (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            propietario_id uuid
                REFERENCES auth.usuario(id) ON DELETE SET NULL,
            nombre varchar(100) NOT NULL,
            apellido varchar(100) NOT NULL,
            documento varchar(50),
            matricula varchar(50),
            taller_nombre varchar(150),
            taller_direccion text,
            taller_telefono varchar(50),
            usuario_id uuid
                REFERENCES auth.usuario(id) ON DELETE SET NULL,
            activo boolean NOT NULL DEFAULT true,
            created_at timestamp NOT NULL DEFAULT now(),
            updated_at timestamp NOT NULL DEFAULT now()
        );
    """)

    # 2.2. Configuracion tecnica del vehiculo
    op.execute("""
        CREATE TABLE IF NOT EXISTS mantenimiento_vehiculo_config (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            vehiculo_id uuid NOT NULL UNIQUE
                REFERENCES fleet.vehiculo(id) ON DELETE CASCADE,
            motorizacion varchar(20)
                CHECK (motorizacion IN ('nafta', 'diesel', 'gnc', 'hibrido', 'electrico')),
            cilindrada int,
            transmision varchar(20)
                CHECK (transmision IN ('manual', 'automatica', 'cvt')),
            version varchar(50),
            notas_tecnicas text,
            created_at timestamp NOT NULL DEFAULT now(),
            updated_at timestamp NOT NULL DEFAULT now()
        );
    """)

    # 2.3. Configuracion de mantenimiento por tenant
    op.execute("""
        CREATE TABLE IF NOT EXISTS tenant.configuracion_mantenimiento (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            control_base_id uuid NOT NULL UNIQUE
                REFERENCES tenant.control_base(id) ON DELETE CASCADE,
            umbral_proximo_km int NOT NULL DEFAULT 2000,
            umbral_proximo_dias int NOT NULL DEFAULT 30,
            umbral_critico_km int NOT NULL DEFAULT 500,
            umbral_critico_dias int NOT NULL DEFAULT 7,
            limite_servicio_limitado_dias int NOT NULL DEFAULT 30,
            limite_fuera_servicio_dias int NOT NULL DEFAULT 60,
            stale_km_dias int NOT NULL DEFAULT 7,
            created_at timestamp NOT NULL DEFAULT now(),
            updated_at timestamp NOT NULL DEFAULT now()
        );
    """)

    # ============================================================
    # 3. SEED: SISTEMAS (15)
    # ============================================================
    op.execute("""
        INSERT INTO mantenimiento_catalogo_sistema (nombre, descripcion, orden)
        SELECT v.nombre, v.descripcion, v.orden
        FROM (VALUES
            ('Eléctrico', 'Batería, alternador, luces, fusibles, cableado', 1),
            ('Motorización', 'Motor, distribución, lubricación', 2),
            ('Suspensión', 'Tren delantero, dirección, alineación y balanceo', 3),
            ('Refrigeración', 'Radiador, bomba de agua, termostato, mangueras, electroventilador', 4),
            ('Frenos', 'Delanteros, traseros, líquido, ABS, freno de mano', 5),
            ('Embrague', 'Disco, placa, rulemán, cable/hidráulico', 6),
            ('Equipo de Gas', 'Tanque, regulador, válvulas, cañerías, conmutador', 7),
            ('Dirección Hidráulica', 'Bomba, líquido, mangueras', 8),
            ('Filtros y Lubricantes', 'Aceite, filtro de aceite, filtro de aire, filtro de combustible, filtro de habitáculo', 9),
            ('Neumáticos / Cubiertas', 'Delantera izq, delantera der, trasera izq, trasera der, auxilio', 10),
            ('Transmisión', 'Caja, diferencial, semiejes', 11),
            ('Escape', 'Caño de escape, catalizador, silenciador', 12),
            ('Carrocería', 'Chapa, pintura, vidrios, paragolpes', 13),
            ('Aire acondicionado / Climatización', 'Compresor, gas, filtro de habitáculo', 14),
            ('Sistema de combustible', 'Bomba, inyectores, tanque', 15)
        ) AS v(nombre, descripcion, orden)
        WHERE NOT EXISTS (
            SELECT 1 FROM mantenimiento_catalogo_sistema s WHERE s.nombre = v.nombre
        );
    """)

    # ============================================================
    # 4. SEED: SUBSISTEMAS (61)
    # ============================================================
    op.execute("""
        INSERT INTO mantenimiento_catalogo_subsistema (sistema_id, nombre, orden)
        SELECT s.id, v.nombre, v.orden
        FROM (VALUES
            -- Eléctrico
            ('Eléctrico', 'Batería', 1),
            ('Eléctrico', 'Alternador', 2),
            ('Eléctrico', 'Luces', 3),
            ('Eléctrico', 'Fusibles y relés', 4),
            ('Eléctrico', 'Cableado', 5),
            -- Motorización
            ('Motorización', 'Motor', 1),
            ('Motorización', 'Distribución', 2),
            ('Motorización', 'Lubricación', 3),
            -- Suspensión
            ('Suspensión', 'Tren delantero', 1),
            ('Suspensión', 'Dirección', 2),
            ('Suspensión', 'Alineación y balanceo', 3),
            -- Refrigeración
            ('Refrigeración', 'Radiador', 1),
            ('Refrigeración', 'Bomba de agua', 2),
            ('Refrigeración', 'Termostato', 3),
            ('Refrigeración', 'Mangueras', 4),
            ('Refrigeración', 'Electroventilador', 5),
            -- Frenos
            ('Frenos', 'Delanteros', 1),
            ('Frenos', 'Traseros', 2),
            ('Frenos', 'Líquido', 3),
            ('Frenos', 'ABS', 4),
            ('Frenos', 'Freno de mano', 5),
            -- Embrague
            ('Embrague', 'Disco', 1),
            ('Embrague', 'Placa', 2),
            ('Embrague', 'Rulemán', 3),
            ('Embrague', 'Cable/hidráulico', 4),
            -- Equipo de Gas
            ('Equipo de Gas', 'Tanque', 1),
            ('Equipo de Gas', 'Regulador', 2),
            ('Equipo de Gas', 'Válvulas', 3),
            ('Equipo de Gas', 'Cañerías', 4),
            ('Equipo de Gas', 'Conmutador', 5),
            -- Dirección Hidráulica
            ('Dirección Hidráulica', 'Bomba', 1),
            ('Dirección Hidráulica', 'Líquido', 2),
            ('Dirección Hidráulica', 'Mangueras', 3),
            -- Filtros y Lubricantes
            ('Filtros y Lubricantes', 'Aceite', 1),
            ('Filtros y Lubricantes', 'Filtro de aceite', 2),
            ('Filtros y Lubricantes', 'Filtro de aire', 3),
            ('Filtros y Lubricantes', 'Filtro de combustible', 4),
            ('Filtros y Lubricantes', 'Filtro de habitáculo', 5),
            -- Neumáticos / Cubiertas
            ('Neumáticos / Cubiertas', 'Delantera izq', 1),
            ('Neumáticos / Cubiertas', 'Delantera der', 2),
            ('Neumáticos / Cubiertas', 'Trasera izq', 3),
            ('Neumáticos / Cubiertas', 'Trasera der', 4),
            ('Neumáticos / Cubiertas', 'Auxilio', 5),
            -- Transmisión
            ('Transmisión', 'Caja', 1),
            ('Transmisión', 'Diferencial', 2),
            ('Transmisión', 'Semiejes', 3),
            -- Escape
            ('Escape', 'Caño de escape', 1),
            ('Escape', 'Catalizador', 2),
            ('Escape', 'Silenciador', 3),
            -- Carrocería
            ('Carrocería', 'Chapa', 1),
            ('Carrocería', 'Pintura', 2),
            ('Carrocería', 'Vidrios', 3),
            ('Carrocería', 'Paragolpes', 4),
            -- Aire acondicionado / Climatización
            ('Aire acondicionado / Climatización', 'Compresor', 1),
            ('Aire acondicionado / Climatización', 'Gas', 2),
            ('Aire acondicionado / Climatización', 'Filtro de habitáculo', 3),
            -- Sistema de combustible
            ('Sistema de combustible', 'Bomba', 1),
            ('Sistema de combustible', 'Inyectores', 2),
            ('Sistema de combustible', 'Tanque', 3)
        ) AS v(sistema_nombre, nombre, orden)
        JOIN mantenimiento_catalogo_sistema s ON s.nombre = v.sistema_nombre
        WHERE NOT EXISTS (
            SELECT 1 FROM mantenimiento_catalogo_subsistema ss
            WHERE ss.sistema_id = s.id AND ss.nombre = v.nombre
        );
    """)

    # ============================================================
    # 5. SEED: COMPONENTES (~102, sin duplicados entre sistemas)
    # ============================================================
    op.execute("""
        INSERT INTO mantenimiento_catalogo_componente (subsistema_id, nombre, orden)
        SELECT ss.id, v.nombre, v.orden
        FROM (VALUES
            -- Eléctrico
            ('Eléctrico', 'Batería', 'Batería', 1),
            ('Eléctrico', 'Alternador', 'Alternador', 1),
            ('Eléctrico', 'Luces', 'Lámpara delantera izq', 1),
            ('Eléctrico', 'Luces', 'Lámpara delantera der', 2),
            ('Eléctrico', 'Luces', 'Lámpara trasera izq', 3),
            ('Eléctrico', 'Luces', 'Lámpara trasera der', 4),
            ('Eléctrico', 'Luces', 'Luz de giro', 5),
            ('Eléctrico', 'Luces', 'Baliza', 6),
            ('Eléctrico', 'Fusibles y relés', 'Fusible', 1),
            ('Eléctrico', 'Fusibles y relés', 'Relé', 2),
            ('Eléctrico', 'Cableado', 'Cableado general', 1),
            -- Motorización (sin refrigeración ni aceite, que van en otros sistemas)
            ('Motorización', 'Motor', 'Bujías', 1),
            ('Motorización', 'Motor', 'Bobina de encendido', 2),
            ('Motorización', 'Motor', 'Correa de accesorios', 3),
            ('Motorización', 'Distribución', 'Correa de distribución', 1),
            ('Motorización', 'Distribución', 'Cadena de distribución', 2),
            ('Motorización', 'Distribución', 'Tensor', 3),
            ('Motorización', 'Lubricación', 'Bomba de aceite', 1),
            -- Suspensión
            ('Suspensión', 'Tren delantero', 'Amortiguador delantero izq', 1),
            ('Suspensión', 'Tren delantero', 'Amortiguador delantero der', 2),
            ('Suspensión', 'Tren delantero', 'Resorte delantero izq', 3),
            ('Suspensión', 'Tren delantero', 'Resorte delantero der', 4),
            ('Suspensión', 'Tren delantero', 'Buje de parrilla', 5),
            ('Suspensión', 'Dirección', 'Cremallera', 1),
            ('Suspensión', 'Dirección', 'Terminal de dirección izq', 2),
            ('Suspensión', 'Dirección', 'Terminal de dirección der', 3),
            ('Suspensión', 'Dirección', 'Bieleta', 4),
            ('Suspensión', 'Alineación y balanceo', 'Alineación', 1),
            ('Suspensión', 'Alineación y balanceo', 'Balanceo', 2),
            -- Refrigeración (todos los componentes de refrigeración van acá)
            ('Refrigeración', 'Radiador', 'Radiador', 1),
            ('Refrigeración', 'Bomba de agua', 'Bomba de agua', 1),
            ('Refrigeración', 'Termostato', 'Termostato', 1),
            ('Refrigeración', 'Mangueras', 'Manguera superior', 1),
            ('Refrigeración', 'Mangueras', 'Manguera inferior', 2),
            ('Refrigeración', 'Electroventilador', 'Electroventilador', 1),
            -- Frenos
            ('Frenos', 'Delanteros', 'Pastillas delanteras', 1),
            ('Frenos', 'Delanteros', 'Discos delanteros', 2),
            ('Frenos', 'Delanteros', 'Caliper delantero izq', 3),
            ('Frenos', 'Delanteros', 'Caliper delantero der', 4),
            ('Frenos', 'Traseros', 'Pastillas traseras', 1),
            ('Frenos', 'Traseros', 'Discos traseros', 2),
            ('Frenos', 'Traseros', 'Caliper trasero izq', 3),
            ('Frenos', 'Traseros', 'Caliper trasero der', 4),
            ('Frenos', 'Líquido', 'Líquido de frenos', 1),
            ('Frenos', 'ABS', 'Sensor ABS delantero izq', 1),
            ('Frenos', 'ABS', 'Sensor ABS delantero der', 2),
            ('Frenos', 'ABS', 'Sensor ABS trasero izq', 3),
            ('Frenos', 'ABS', 'Sensor ABS trasero der', 4),
            ('Frenos', 'Freno de mano', 'Pastillas de freno de mano', 1),
            ('Frenos', 'Freno de mano', 'Cable de freno de mano', 2),
            -- Embrague
            ('Embrague', 'Disco', 'Disco de embrague', 1),
            ('Embrague', 'Placa', 'Placa de presión', 1),
            ('Embrague', 'Rulemán', 'Rulemán de empuje', 1),
            ('Embrague', 'Cable/hidráulico', 'Cable de embrague', 1),
            ('Embrague', 'Cable/hidráulico', 'Cilindro hidráulico', 2),
            -- Equipo de Gas
            ('Equipo de Gas', 'Tanque', 'Tanque de GNC', 1),
            ('Equipo de Gas', 'Regulador', 'Regulador', 1),
            ('Equipo de Gas', 'Válvulas', 'Válvula de carga', 1),
            ('Equipo de Gas', 'Válvulas', 'Válvula de corte', 2),
            ('Equipo de Gas', 'Cañerías', 'Cañería de alta', 1),
            ('Equipo de Gas', 'Cañerías', 'Cañería de baja', 2),
            ('Equipo de Gas', 'Conmutador', 'Conmutador', 1),
            -- Dirección Hidráulica (sin cremallera, que va en Suspensión)
            ('Dirección Hidráulica', 'Bomba', 'Bomba hidráulica', 1),
            ('Dirección Hidráulica', 'Líquido', 'Líquido hidráulico', 1),
            ('Dirección Hidráulica', 'Mangueras', 'Manguera de presión', 1),
            ('Dirección Hidráulica', 'Mangueras', 'Manguera de retorno', 2),
            -- Filtros y Lubricantes (todos los filtros + aceite)
            ('Filtros y Lubricantes', 'Aceite', 'Aceite de motor', 1),
            ('Filtros y Lubricantes', 'Filtro de aceite', 'Filtro de aceite', 1),
            ('Filtros y Lubricantes', 'Filtro de aire', 'Filtro de aire', 1),
            ('Filtros y Lubricantes', 'Filtro de combustible', 'Filtro de combustible', 1),
            ('Filtros y Lubricantes', 'Filtro de habitáculo', 'Filtro de habitáculo', 1),
            -- Neumáticos / Cubiertas
            ('Neumáticos / Cubiertas', 'Delantera izq', 'Cubierta delantera izquierda', 1),
            ('Neumáticos / Cubiertas', 'Delantera der', 'Cubierta delantera derecha', 2),
            ('Neumáticos / Cubiertas', 'Trasera izq', 'Cubierta trasera izquierda', 3),
            ('Neumáticos / Cubiertas', 'Trasera der', 'Cubierta trasera derecha', 4),
            ('Neumáticos / Cubiertas', 'Auxilio', 'Cubierta de auxilio', 5),
            -- Transmisión
            ('Transmisión', 'Caja', 'Caja de cambios', 1),
            ('Transmisión', 'Diferencial', 'Diferencial', 1),
            ('Transmisión', 'Semiejes', 'Semieje izquierdo', 1),
            ('Transmisión', 'Semiejes', 'Semieje derecho', 2),
            -- Escape
            ('Escape', 'Caño de escape', 'Caño de escape', 1),
            ('Escape', 'Catalizador', 'Catalizador', 1),
            ('Escape', 'Silenciador', 'Silenciador', 1),
            -- Carrocería (paragolpes solo en Paragolpes, no en Chapa)
            ('Carrocería', 'Chapa', 'Capot', 1),
            ('Carrocería', 'Chapa', 'Baúl', 2),
            ('Carrocería', 'Pintura', 'Pintura general', 1),
            ('Carrocería', 'Vidrios', 'Parabrisas', 1),
            ('Carrocería', 'Vidrios', 'Luneta trasera', 2),
            ('Carrocería', 'Vidrios', 'Vidrios laterales', 3),
            ('Carrocería', 'Paragolpes', 'Paragolpes delantero', 1),
            ('Carrocería', 'Paragolpes', 'Paragolpes trasero', 2),
            -- Aire acondicionado / Climatización
            ('Aire acondicionado / Climatización', 'Compresor', 'Compresor', 1),
            ('Aire acondicionado / Climatización', 'Gas', 'Gas refrigerante', 1),
            ('Aire acondicionado / Climatización', 'Filtro de habitáculo', 'Filtro de habitáculo', 1),
            -- Sistema de combustible
            ('Sistema de combustible', 'Bomba', 'Bomba de combustible', 1),
            ('Sistema de combustible', 'Inyectores', 'Inyector 1', 1),
            ('Sistema de combustible', 'Inyectores', 'Inyector 2', 2),
            ('Sistema de combustible', 'Inyectores', 'Inyector 3', 3),
            ('Sistema de combustible', 'Inyectores', 'Inyector 4', 4),
            ('Sistema de combustible', 'Tanque', 'Tanque de combustible', 1)
        ) AS v(sistema_nombre, subsistema_nombre, nombre, orden)
        JOIN mantenimiento_catalogo_sistema s ON s.nombre = v.sistema_nombre
        JOIN mantenimiento_catalogo_subsistema ss
            ON ss.sistema_id = s.id AND ss.nombre = v.subsistema_nombre
        WHERE NOT EXISTS (
            SELECT 1 FROM mantenimiento_catalogo_componente c
            WHERE c.subsistema_id = ss.id AND c.nombre = v.nombre
        );
    """)

    # ============================================================
    # 6. SEED: CONTROLES GENERICOS (7)
    # ============================================================
    op.execute("""
        INSERT INTO mantenimiento_catalogo_control
            (nombre, tipo, unidad, rango_normal, orden)
        SELECT v.nombre, v.tipo, v.unidad, v.rango_normal, v.orden
        FROM (VALUES
            ('Estado visual', 'visual', NULL, 'OK / desgaste / daño', 1),
            ('Nivel de líquido', 'instrumental', '%', '50-100', 2),
            ('Espesor', 'instrumental', 'mm', '>= 3', 3),
            ('Presión', 'instrumental', 'PSI', '28-36', 4),
            ('Profundidad', 'instrumental', 'mm', '>= 1.6', 5),
            ('Kilometraje', 'documental', 'km', NULL, 6),
            ('Fecha', 'documental', 'días', NULL, 7)
        ) AS v(nombre, tipo, unidad, rango_normal, orden)
        WHERE NOT EXISTS (
            SELECT 1 FROM mantenimiento_catalogo_control c
            WHERE c.nombre = v.nombre AND c.componente_id IS NULL
        );
    """)

    # ============================================================
    # 7. SEED: CHECKLIST DE INSPECCION (16)
    # ============================================================
    op.execute("""
        INSERT INTO mantenimiento_checklist_inspeccion
            (nombre, tipo_inspeccion, tipo_respuesta, opciones, severidad_default, orden)
        SELECT v.nombre, v.tipo_inspeccion, v.tipo_respuesta,
               v.opciones::jsonb, v.severidad_default, v.orden
        FROM (VALUES
            ('Nivel de aceite de motor', 'inicio', 'nivel',
                '["ok", "bajo", "crítico"]', 'alta', 1),
            ('Nivel de refrigerante', 'inicio', 'nivel',
                '["ok", "bajo", "crítico"]', 'alta', 2),
            ('Nivel de líquido de frenos', 'inicio', 'nivel',
                '["ok", "bajo", "crítico"]', 'critica', 3),
            ('Estado cubierta delantera izquierda', 'ambos', 'estado_visual',
                '["ok", "desgastada", "pinchada"]', 'media', 4),
            ('Estado cubierta delantera derecha', 'ambos', 'estado_visual',
                '["ok", "desgastada", "pinchada"]', 'media', 5),
            ('Estado cubierta trasera izquierda', 'ambos', 'estado_visual',
                '["ok", "desgastada", "pinchada"]', 'media', 6),
            ('Estado cubierta trasera derecha', 'ambos', 'estado_visual',
                '["ok", "desgastada", "pinchada"]', 'media', 7),
            ('Luces delanteras', 'ambos', 'ok_novedad', NULL, 'media', 8),
            ('Luces traseras', 'ambos', 'ok_novedad', NULL, 'media', 9),
            ('Balizas', 'ambos', 'ok_novedad', NULL, 'alta', 10),
            ('Espejos retrovisores', 'ambos', 'ok_novedad', NULL, 'baja', 11),
            ('Limpiaparabrisas', 'ambos', 'ok_novedad', NULL, 'baja', 12),
            ('Bocina', 'ambos', 'ok_novedad', NULL, 'media', 13),
            ('Documentación a bordo', 'inicio', 'si_no', NULL, 'alta', 14),
            ('Extintor', 'inicio', 'si_no', NULL, 'critica', 15),
            ('Observaciones generales', 'ambos', 'texto_libre', NULL, NULL, 16)
        ) AS v(nombre, tipo_inspeccion, tipo_respuesta, opciones, severidad_default, orden)
        WHERE NOT EXISTS (
            SELECT 1 FROM mantenimiento_checklist_inspeccion ci WHERE ci.nombre = v.nombre
        );
    """)

    # ============================================================
    # 8. VINCULAR CHECKLIST CON COMPONENTES DE CUBIERTAS
    # ============================================================
    op.execute("""
        UPDATE mantenimiento_checklist_inspeccion ci
        SET componente_id = c.id
        FROM mantenimiento_catalogo_componente c
        WHERE ci.nombre = 'Estado cubierta delantera izquierda'
          AND c.nombre = 'Cubierta delantera izquierda'
          AND ci.componente_id IS NULL;
    """)
    op.execute("""
        UPDATE mantenimiento_checklist_inspeccion ci
        SET componente_id = c.id
        FROM mantenimiento_catalogo_componente c
        WHERE ci.nombre = 'Estado cubierta delantera derecha'
          AND c.nombre = 'Cubierta delantera derecha'
          AND ci.componente_id IS NULL;
    """)
    op.execute("""
        UPDATE mantenimiento_checklist_inspeccion ci
        SET componente_id = c.id
        FROM mantenimiento_catalogo_componente c
        WHERE ci.nombre = 'Estado cubierta trasera izquierda'
          AND c.nombre = 'Cubierta trasera izquierda'
          AND ci.componente_id IS NULL;
    """)
    op.execute("""
        UPDATE mantenimiento_checklist_inspeccion ci
        SET componente_id = c.id
        FROM mantenimiento_catalogo_componente c
        WHERE ci.nombre = 'Estado cubierta trasera derecha'
          AND c.nombre = 'Cubierta trasera derecha'
          AND ci.componente_id IS NULL;
    """)


def downgrade():
    op.execute("DROP TABLE IF EXISTS tenant.configuracion_mantenimiento;")
    op.execute("DROP TABLE IF EXISTS mantenimiento_vehiculo_config;")
    op.execute("DROP TABLE IF EXISTS fleet.encargado;")
    op.execute("DROP TABLE IF EXISTS mantenimiento_checklist_inspeccion;")
    op.execute("DROP TABLE IF EXISTS mantenimiento_catalogo_componente_compatibilidad;")
    op.execute("DROP TABLE IF EXISTS mantenimiento_catalogo_control;")
    op.execute("DROP TABLE IF EXISTS mantenimiento_catalogo_componente;")
    op.execute("DROP TABLE IF EXISTS mantenimiento_catalogo_subsistema;")
    op.execute("DROP TABLE IF EXISTS mantenimiento_catalogo_sistema;")
DELIMITER //

CREATE OR REPLACE PROCEDURE proc_stock_summary(
    IN begin_date DATETIME,
    IN end_date DATETIME,
    IN is_add BOOLEAN
)
BEGIN
    -- Drop and create temporary table
    DROP TEMPORARY TABLE IF EXISTS temp_materials_constn_summary;
    CREATE TEMPORARY TABLE temp_materials_constn_summary AS
    SELECT
        d.material_id,
        tg.constn_site_id,
        mat.specification_id AS spec,
        SUM(CASE WHEN tg.transaction_type = 'OUT' THEN d.quantity WHEN tg.transaction_type = 'IN' THEN (d.quantity * -1) ELSE 0 END) AS quantity,
        SUM(CASE WHEN tg.transaction_type = 'OUT' THEN d.all_unit WHEN tg.transaction_type = 'IN' THEN (d.all_unit * -1) ELSE 0 END) AS total_unit
    FROM
        trans_translogdetail AS d
        INNER JOIN trans_translog AS tg ON d.translog_id = tg.id
        INNER JOIN stock_materials AS mat ON mat.id = d.material_id
    WHERE
        tg.build_date BETWEEN begin_date AND end_date
        AND d.remark NOT LIKE '%#%'
        AND tg.constn_site_id <> 1
    GROUP BY
        d.material_id,
        mat.specification_id,
        tg.constn_site_id;

    -- Insert into temp_materials_constn_summary from temp_materials_summary
    INSERT INTO temp_materials_constn_summary (material_id, constn_site_id, spec, quantity, total_unit)
    SELECT
        d.material_id,
        2 as constn_site_id,
        mat.specification_id AS spec,
        SUM(CASE WHEN tg.transaction_type = 'IN' THEN d.quantity WHEN tg.transaction_type = 'OUT' THEN (d.quantity * -1) ELSE 0 END) AS quantity,
        SUM(CASE WHEN tg.transaction_type = 'IN' THEN d.all_unit WHEN tg.transaction_type = 'OUT' THEN (d.all_unit * -1) ELSE 0 END) AS total_unit
    FROM
        trans_translogdetail AS d
        INNER JOIN trans_translog AS tg ON d.translog_id = tg.id
        INNER JOIN stock_materials AS mat ON mat.id = d.material_id
    WHERE
        tg.build_date BETWEEN begin_date AND end_date
    GROUP BY
        d.material_id,
        mat.specification_id;

    IF is_add  THEN
        INSERT INTO stock_stock (material_id, siteinfo_id, quantity, unit, total_unit)
        SELECT
            tms.material_id,
            tms.constn_site_id,
            tms.quantity,
            tms.spec,
            tms.total_unit
        FROM temp_materials_constn_summary AS tms
        ON DUPLICATE KEY UPDATE
            stock_stock.quantity = stock_stock.quantity + VALUES(quantity),
            stock_stock.total_unit = stock_stock.total_unit + VALUES(total_unit);
         SELECT 'Inserted into stock_stock (is_add = TRUE):', ROW_COUNT();
    ELSE
        INSERT INTO stock_stock (material_id, siteinfo_id, quantity, unit, total_unit)
        SELECT
            tms.material_id,
            tms.constn_site_id,
            -tms.quantity,
            tms.spec,
            -tms.total_unit
        FROM temp_materials_constn_summary AS tms
        ON DUPLICATE KEY UPDATE
            stock_stock.quantity = stock_stock.quantity + VALUES(quantity),
            stock_stock.total_unit = stock_stock.total_unit + VALUES(total_unit);
        SELECT 'Inserted into stock_stock (is_add = FALSE):', ROW_COUNT();
    END IF;

    DROP TEMPORARY TABLE IF EXISTS temp_materials_constn_summary;

	INSERT INTO stock_stock (material_id, siteinfo_id, quantity,unit, total_unit)
	SELECT
	    st.id AS material_id,
	    st.siteinfo_id,
	    SUM(st.quantity) AS quantity,
	    0 AS unit ,
	    SUM(st.total_unit) AS total_unit
	FROM
		(
            SELECT mat.id , sum_mat.* FROM (
                SELECT mat.mat_code , st.siteinfo_id, SUM(st.quantity) AS quantity , SUM(st.total_unit) AS total_unit
                FROM stock_stock AS st
                INNER JOIN stock_materials AS mat ON st.material_id = mat.id
                WHERE  mat.specification_id BETWEEN 0 AND 22
                GROUP BY mat.mat_code , st.siteinfo_id
            ) AS sum_mat
            INNER JOIN stock_materials AS mat  ON mat.mat_code = sum_mat.mat_code AND mat.specification_id =23
		)   AS st
	GROUP BY st.id,st.siteinfo_id
	ON DUPLICATE KEY UPDATE
	    stock_stock.quantity = VALUES(quantity),
	    stock_stock.unit = 0,
	    stock_stock.total_unit = VALUES(total_unit);

	INSERT INTO stock_stock (material_id, siteinfo_id, quantity,unit, total_unit)
	SELECT
	    462 AS material_id,
	    st.siteinfo_id,
	    SUM(st.quantity) AS quantity,
	    0 AS unit ,
	    SUM(st.total_unit) AS total_unit
	FROM
		(
        SELECT st.siteinfo_id, st.quantity ,st.total_unit
        FROM stock_stock AS st
        INNER JOIN stock_materials AS mat ON st.material_id = mat.id
        WHERE mat.mat_code in ('2301','2302')
		)   AS st
	GROUP BY st.siteinfo_id
	ON DUPLICATE KEY UPDATE
	    stock_stock.quantity = VALUES(quantity),
	    stock_stock.unit = 0,
	    stock_stock.total_unit = VALUES(total_unit);

	INSERT INTO stock_stock (material_id, siteinfo_id, quantity,unit, total_unit)
	SELECT
	    st.material_id,
	    941,
	    SUM(st.quantity) AS quantity,
	    0 AS unit ,
	    SUM(st.total_unit) AS total_unit
	FROM stock_stock AS st
    INNER JOIN stock_siteinfo AS info ON st.siteinfo_id = info.id
    where info.`code` in ('F002','F003')
	GROUP BY st.material_id
	ON DUPLICATE KEY UPDATE
	    stock_stock.quantity = VALUES(quantity),
	    stock_stock.unit = 0,
	    stock_stock.total_unit = VALUES(total_unit);

    delete stock_stock FROM stock_stock where siteinfo_id in (940,942) ;
END //

DELIMITER ;

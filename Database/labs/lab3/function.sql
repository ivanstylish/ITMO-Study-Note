-- Функция на языке PL/pgSQL для автоматического обновление статуса миссии.
-- Связь между таблицами:
-- MISSION - mission_id (FK) - MISSIONPHASE - mission_id (FK)
-- Статусы: active, completed, planned.

ALTER TABLE MISSION
ADD COLUMN STATUS VARCHAR(20) CHECK (STATUS IN ('active', 'completed', 'planned'));

CREATE OR REPLACE FUNCTION update_mission_status()
RETURNS TRIGGER AS $$
DECLARE
    total_phases INT; -- Общее количество этапов текущей задачи
    completed_phases INT; -- Количество завершенных этапов текущей задачи
BEGIN
    -- Получить общее количество этапов текущей задачи
    SELECT COUNT(*) INTO total_phases
    FROM MISSIONPHASE
    WHERE MISSION_ID = NEW.MISSION_ID;

    -- Получение количества завершенных этапов текущей задачи    SELECT COUNT(*) INTO completed_phases
    FROM MISSIONPHASE
    WHERE MISSION_ID = NEW.MISSION_ID
    AND STATUS = 'completed';

    -- Если все этапы завершены, обновите статус задачи до “completed”
    IF total_phases = completed_phases AND total_phases > 0 THEN
        UPDATE MISSION
        SET STATUS = 'completed'
        WHERE MISSION_ID = NEW.MISSION_ID;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER mission_phase_status_trigger
AFTER UPDATE OF STATUS ON MISSIONPHASE
FOR EACH ROW
WHEN (NEW.STATUS = 'completed')  -- Срабатывает только при обновлении статуса до "completed".
EXECUTE FUNCTION update_mission_status();

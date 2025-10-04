"""
NoSQL Database Service - простая и надежная JSON-based база данных
Никаких блокировок, никаких thread limit проблем!
"""
import json
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class NoSQLDatabase:
    """NoSQL база данных на основе JSON файлов"""
    
    def __init__(self, db_dir: str = "nosql_db"):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)
        
        # Файлы для разных коллекций
        self.collections = {
            'wars': self.db_dir / 'wars.json',
            'users': self.db_dir / 'users.json',
            'clans': self.db_dir / 'clans.json',
            'attacks': self.db_dir / 'attacks.json',
            'stats': self.db_dir / 'stats.json'
        }
        
        # Инициализация файлов
        asyncio.create_task(self._init_collections())
        
        logger.info(f"🗄️ NoSQL Database инициализирована в папке: {self.db_dir}")
    
    async def _init_collections(self):
        """Инициализация коллекций"""
        for name, file_path in self.collections.items():
            if not file_path.exists():
                await self._write_json(file_path, {})
                logger.info(f"📁 Создана коллекция: {name}")
    
    async def _read_json(self, file_path: Path) -> Dict:
        """Чтение JSON файла"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return json.loads(content) if content.strip() else {}
            return {}
        except Exception as e:
            logger.warning(f"Ошибка чтения {file_path}: {e}")
            return {}
    
    async def _write_json(self, file_path: Path, data: Dict):
        """Запись JSON файла"""
        try:
            # Создание backup
            if file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                with open(file_path, 'r', encoding='utf-8') as src:
                    content = src.read()
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(content)
            
            # Запись новых данных
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            logger.error(f"Ошибка записи {file_path}: {e}")
            raise
    
    async def save_war(self, war_data: Dict) -> bool:
        """Сохранение войны"""
        try:
            wars = await self._read_json(self.collections['wars'])
            
            war_id = war_data.get('end_time', str(datetime.now().timestamp()))
            wars[war_id] = {
                **war_data,
                'saved_at': datetime.now().isoformat(),
                'id': war_id
            }
            
            await self._write_json(self.collections['wars'], wars)
            logger.debug(f"✅ Война сохранена: {war_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения войны: {e}")
            return False
    
    async def war_exists(self, end_time: str) -> bool:
        """Проверка существования войны"""
        try:
            wars = await self._read_json(self.collections['wars'])
            return end_time in wars
        except:
            return False
    
    async def get_wars_count(self) -> int:
        """Получение количества войн"""
        try:
            wars = await self._read_json(self.collections['wars'])
            return len(wars)
        except:
            return 0
    
    async def save_clan(self, clan_data: Dict) -> bool:
        """Сохранение клана"""
        try:
            clans = await self._read_json(self.collections['clans'])
            
            clan_tag = clan_data.get('tag', 'unknown')
            clans[clan_tag] = {
                **clan_data,
                'last_updated': datetime.now().isoformat()
            }
            
            await self._write_json(self.collections['clans'], clans)
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения клана: {e}")
            return False
    
    async def save_attack(self, attack_data: Dict) -> bool:
        """Сохранение атаки"""
        try:
            attacks = await self._read_json(self.collections['attacks'])
            
            attack_id = f"{attack_data.get('war_id', '')}_{attack_data.get('attacker_tag', '')}_{attack_data.get('order', 0)}"
            attacks[attack_id] = {
                **attack_data,
                'saved_at': datetime.now().isoformat()
            }
            
            await self._write_json(self.collections['attacks'], attacks)
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения атаки: {e}")
            return False
    
    async def update_stats(self, stats: Dict) -> bool:
        """Обновление статистики"""
        try:
            current_stats = await self._read_json(self.collections['stats'])
            current_stats.update({
                **stats,
                'last_updated': datetime.now().isoformat()
            })
            
            await self._write_json(self.collections['stats'], current_stats)
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления статистики: {e}")
            return False
    
    async def get_stats(self) -> Dict:
        """Получение статистики"""
        try:
            return await self._read_json(self.collections['stats'])
        except:
            return {}
    
    async def backup_database(self) -> str:
        """Создание backup всей базы данных"""
        try:
            backup_dir = self.db_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(exist_ok=True)
            
            for name, file_path in self.collections.items():
                if file_path.exists():
                    backup_file = backup_dir / f"{name}.json"
                    data = await self._read_json(file_path)
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(data, indent=2, ensure_ascii=False))
            
            logger.info(f"💾 Backup создан: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания backup: {e}")
            return ""
    
    async def get_database_info(self) -> Dict:
        """Получение информации о базе данных"""
        info = {
            'database_type': 'NoSQL JSON',
            'collections': {},
            'total_size_mb': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            total_size = 0
            for name, file_path in self.collections.items():
                if file_path.exists():
                    size = file_path.stat().st_size
                    total_size += size
                    
                    data = await self._read_json(file_path)
                    info['collections'][name] = {
                        'records': len(data),
                        'size_bytes': size,
                        'file_path': str(file_path)
                    }
                else:
                    info['collections'][name] = {
                        'records': 0,
                        'size_bytes': 0,
                        'file_path': str(file_path)
                    }
            
            info['total_size_mb'] = round(total_size / 1024 / 1024, 2)
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о БД: {e}")
        
        return info


# Совместимость со старым DatabaseService
class NoSQLDatabaseService:
    """Обертка для совместимости с существующим кодом"""
    
    def __init__(self, db_path: str = None):
        # Игнорируем db_path, используем NoSQL
        self.nosql_db = NoSQLDatabase()
        logger.info("🚀 NoSQL Database Service инициализирован!")
    
    async def init_db(self):
        """Инициализация (для совместимости)"""
        logger.info("✅ NoSQL база данных готова к работе!")
        return True
    
    async def save_war(self, war) -> bool:
        """Сохранение войны (адаптер)"""
        try:
            war_data = {
                'end_time': war.end_time,
                'opponent_name': war.opponent_name,
                'team_size': war.team_size,
                'clan_stars': war.clan_stars,
                'opponent_stars': war.opponent_stars,
                'clan_destruction': war.clan_destruction,
                'opponent_destruction': war.opponent_destruction,
                'clan_attacks_used': war.clan_attacks_used,
                'result': war.result,
                'is_cwl_war': war.is_cwl_war,
                'total_violations': war.total_violations,
                'attacks_by_member': war.attacks_by_member
            }
            
            return await self.nosql_db.save_war(war_data)
            
        except Exception as e:
            logger.error(f"❌ Ошибка в save_war адаптере: {e}")
            return False
    
    async def war_exists(self, end_time: str) -> bool:
        """Проверка существования войны"""
        return await self.nosql_db.war_exists(end_time)
    
    async def get_wars_count(self) -> int:
        """Получение количества войн"""
        return await self.nosql_db.get_wars_count()
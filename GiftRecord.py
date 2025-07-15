import boto3
from botocore.exceptions import ClientError
from dataclasses import dataclass
from datetime import datetime
import time
from typing import Optional, Dict, Any


@dataclass
class GiftRecord:
    user_id: str
    event_type: str
    gift_type: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    gift_id: Optional[str] = None
    created_at: Optional[str] = None
    opened: bool = False
    opened_at: str = None
    status: str = "ACTIVE"

    def __post_init__(self):
        if self.created_at == None:
            self.created_at = self.generate_iso_timestamp()
        if self.gift_id == None:
            self.gift_id = self.generate_gift_id()
    
    def generate_gift_id(self) -> str:
        """Generate a gift ID with timestamp"""
        timestamp = int(time.time() * 1000)  # milliseconds
        return f"gift_{timestamp}"


    def generate_iso_timestamp(self) -> str:
        """Generate ISO format timestamp"""
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert dataclass to DynamoDB item format"""
        # Convert field names to match DynamoDB schema
        item = {
            'userId': self.user_id,
            'giftId': self.gift_id,
            'createdAt': self.created_at,
            'description': self.description,
            'eventType': self.event_type,
            'giftType': self.gift_type,
            'ipAddress': self.ip_address,
            'opened': self.opened,
            'openedAt': self.opened_at,
            'status': self.status
        }
        return item
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> 'GiftRecord':
        """Create GiftRecord from DynamoDB item"""
        return cls(
            user_id=item['userId'],
            gift_id=item['giftId'],
            created_at=item['createdAt'],
            description=item['description'],
            event_type=item['eventType'],
            gift_type=item['giftType'],
            ip_address=item['ipAddress'],
            opened=item['opened'],
            opened_at=item['openedAt'],
            status=item['status']
        )
    
    def save_to_dynamodb(self, table_name: str) -> bool:
        try:
            dynamodb = boto3.resource("dynamodb")
            table = dynamodb.Table(table_name)

            table.put_item(Item=self.to_dynamodb_item())
            return True
        except ClientError as e:
            return False
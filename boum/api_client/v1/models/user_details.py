from dataclasses import dataclass


@dataclass
class UserDetails:
    data: dict | None = None

    def to_payload(self) -> dict[str, str]:
        payload = {}
        if self.data is not None:
            payload = self.data
        return payload

    @staticmethod
    def from_payload(payload: dict[str, str]) -> 'UserDetails':
        return UserDetails(
            data=payload
        )

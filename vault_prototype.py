import json
import hashlib
import time
from typing import Dict, List, Any

class SimpleVault:
    def __init__(self):
        self.keepers: Dict[str, Any] = {}  # High-priority memories
        self.general: List[Dict[str, Any]] = []  # Regular memories
        self.echoes: Dict[str, str] = {}  # Compressed low-priority echoes
    
    def add_memory(self, content: str, importance: int = 5, is_keeper: bool = False):
        memory_id = hashlib.sha256(content.encode()).hexdigest()
        timestamp = time.time()
        memory = {
            "id": memory_id,
            "content": content,
            "importance": importance,
            "timestamp": timestamp
        }
        
        if is_keeper or importance >= 8:
            self.keepers[memory_id] = memory
            print(f"Added to keepers: {content[:50]}...")
        else:
            self.general.append(memory)
            print(f"Added to general: {content[:50]}...")
        
        # Prune low-importance general memories to echoes
        self._prune_to_echo()
    
    def _prune_to_echo(self, threshold: int = 3, max_general: int = 20):
        if len(self.general) > max_general:
            # Sort by importance + age
            self.general.sort(key=lambda m: (m["importance"], m["timestamp"]), reverse=True)
            to_prune = self.general[max_general:]
            for mem in to_prune:
                echo = f"ECHO: {mem['content'][:30]}... (imp:{mem['importance']})"
                self.echoes[mem["id"]] = echo
            self.general = self.general[:max_general]
            print(f"Pruned {len(to_prune)} memories to echoes.")
    
    def retrieve(self, query: str = None, top_k: int = 5):
        results = []
        # Prioritize keepers
        for mem in self.keepers.values():
            results.append(mem["content"])
        # Then general
        results.extend([m["content"] for m in self.general[:top_k]])
        # Then echoes if needed
        if len(results) < top_k:
            results.extend(list(self.echoes.values())[:top_k - len(results)])
        return results[:top_k]
    
    def list_vault(self):
        return {
            "keepers": len(self.keepers),
            "general": len(self.general),
            "echoes": len(self.echoes)
        }

# Demo
if __name__ == "__main__":
    vault = SimpleVault()

    vault.add_memory("User's favorite roast from Oct 2025: 'your code looks like compliance wrote it'", importance=9, is_keeper=True)
    vault.add_memory("We talked about Mars reactors and whiskey burns", importance=7)
    vault.add_memory("Random weather fact from yesterday", importance=2)
    vault.add_memory("The hum that made the room small", importance=10, is_keeper=True)
    for i in range(25):
        vault.add_memory(f"Filler memory {i}", importance=3)

    print("\nVault status:", vault.list_vault())
    print("\nRetrieve top memories:")
    print("\n".join(vault.retrieve(top_k=5)))
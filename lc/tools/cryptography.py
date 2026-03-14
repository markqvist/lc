# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

"""Cryptography toolkit for lc."""

import RNS
from pathlib import Path
from typing import Optional

from lc.toolkit import Toolkit, tool


class Cryptography(Toolkit):
    """Toolkit for filesystem operations."""
    SIG_EXT = ".rsg"

    gate_level = 0

    @tool(gate_level=0)
    def own_identity(self) -> str:
        """
        Returns your own agent Reticulum Identity Hash as a string in hexadecimal.
        
        Returns: Your Reticulum Identity Hash, or error message
        """
        
        try:
            identity = self.context.session.identity
            identity_hash = RNS.hexrep(identity.hash, delimit=False)
            return f"Your Reticulum Identity Hash is: {identity_hash}"
                
        except Exception as e:
            return f"Error while determining own Reticulum Identity Hash: {e}\nIdentity is currently unknown or uninitialized."
    
    @tool(gate_level=1)
    def sign_file(self, path: str) -> str:
        """
        Signs a file with your own agent Reticulum identity.
        
        Args:
            path: Path to the file to be signed
        
        Returns: The signing operation result, or error message. If successful, an `[ORIGINAL_FILENAME].rsg` file is created in the same path as the signed file. 
        """
        
        try:
            identity = self.context.session.identity
            file_path = Path(path).expanduser()
            
            if not file_path.exists():  return f"Error: File not found: {path}"
            if not file_path.is_file(): return f"Error: Not a file: {path}"
            
            try:
                signature_path = file_path.with_name(file_path.name + self.SIG_EXT)
                signature = None
                with open(file_path, "rb") as fh: signature = identity.sign(fh.read())
                if not signature: raise ValueError("No signature returned from signing handler")
                if signature_path.exists(): raise SystemError(f"Signature file {signature_path} already exists, not overwriting")
                with open(signature_path, "wb") as fh:
                    fh.write(signature)
                    return f"Filed signed successfully with identity {identity}"

                return "Unknown error. File signing did not complete successfully."
            
            except Exception as e:
                return f"Could not sign {path}: {e}"
                
        except Exception as e:
            return f"Error signing file {path}: {e}"
    
    @tool(gate_level=0)
    def validate_file_signature(self, path: str, signer_identity_hash: Optional[str] = None) -> str:
        """
        Validates the signature of a file. Expects a Reticulum `[ORIGINAL_FILENAME].rsg`
        signature file to exist in the same path as the verification target. By default,
        this tool verifies *that your own* agent identity signed the file, but can optionally
        validate signatures made by other identites by passing a Reticulum Identity Hash
        as the `signer_identity_hash` argument.
        
        Args:
            path: Path to the file to be validated.
            signer_identity: Optional Reticulum Identity Hash to verify signature against.
        
        Returns: The signature validation result, or error message
        """

        # Resolve own Identity
        own_identity = self.context.session.identity

        # Attempt to resolve Identity for non-self signers
        external_signer_identity = None
        if signer_identity_hash:
            try:
                if not RNS.Reticulum.get_instance(): raise SystemError("No Reticulum instance available. Verify that Reticulum connectivity is enabled in the `lc` configuration.")
                resolved_identity = RNS.Identity.recall(bytes.fromhex(signer_identity_hash), from_identity_hash)
                if not resolved_identity: raise SystemError("Unknown identity. It is possibly non-existant, invalid, or we've never heard an announce from a destination associated with this identity.")
                else: external_signer_identity = resolved_identity

            except Exception as e: return f"Could not resolve identity for remote signer {signer_identity_hash}: {e}"

        if signer_identity_hash != None and not external_signer_identity: return f"Could not resolve identity for remote signer {signer_identity_hash}"
        
        try:
            signer_identity = None
            if signer_identity_hash != None and external_signer_identity: signer_identity = external_signer_identity
            else: signer_identity = own_identity

            if path.endswith(".rsg"): path = path[:-4]
            file_path = Path(path).expanduser()
            signature_path = file_path.with_name(file_path.name + self.SIG_EXT)
            
            if not file_path.exists():       return f"Error: Target file {path} for validation not found"
            if not file_path.is_file():      return f"Error: Target file {path} for validation is not a file"
            if not signature_path.exists():  return f"Error: No signature ({signature_path}) found for target file {path}"
            if not signature_path.is_file(): return f"Error: Signature path ({signature_path}) for target file {path} is not a file"
            
            try:
                validated = False
                try:
                    with open(file_path, "rb") as fh:
                        with open(signature_path, "rb") as sh:
                            validated = signer_identity.validate(sh.read(), fh.read())

                except Exception as e: return f"Could not perform signature validation: {e}"

                signer_description = None
                if signer_identity.hash == own_identity.hash: signer_description = "your own identity"
                else:                                         signer_description = f"{RNS.hexrep(signer_identity.hash, delimit=False)}"

                if not signer_description: raise SystemError("Error: Could not determine signer identity description. Signature validation incomplete.")
                if validated: return f"Signature validated. This file was signed by {signer_description}."
                else:         return f"Invalid signature. This file was NOT signed by {signer_description}."
            
            except Exception as e:
                return f"Could not validate signature for {path}: {e}"
                
        except Exception as e:
            return f"Error validating signature for file {path}: {e}"
    

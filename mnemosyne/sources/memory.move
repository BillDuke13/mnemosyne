module mnemosyne::memory {
    use std::string::String;
    use sui::object;
    use sui::table;
    use sui::tx_context::TxContext;
    use sui::tx_context;
    use sui::transfer;

    /// Stores metadata for a known person and the Walrus blob identifier that holds memory content.
    public struct MemoryEntry has store, drop {
        label: String,
        relationship: String,
        walrus_blob_id: String,
        last_interaction_unix_ms: u64,
        notes_hash: vector<u8>,
    }

    /// Shared registry of memories keyed by incremental numeric IDs.
    public struct MemoryBook has key {
        id: object::UID,
        owner: address,
        next_entry_id: u64,
        entries: table::Table<u64, MemoryEntry>,
    }

    const ENotOwner: u64 = 1;
    const EEntryNotFound: u64 = 2;

    /// Initialize a shared MemoryBook owned by the caller.
    /// The caller becomes the owner and controller for write operations.
    public entry fun create_book(ctx: &mut TxContext) {
        let sender = tx_context::sender(ctx);
        let book = MemoryBook {
            id: object::new(ctx),
            owner: sender,
            next_entry_id: 0,
            entries: table::new(ctx),
        };
        transfer::share_object(book);
    }

    /// Create a new memory entry. Returns the entry ID.
    public entry fun create_entry(
        book: &mut MemoryBook,
        label: String,
        relationship: String,
        walrus_blob_id: String,
        last_interaction_unix_ms: u64,
        notes_hash: vector<u8>,
        ctx: &mut TxContext,
    ): u64 {
        let sender = tx_context::sender(ctx);
        assert!(sender == book.owner, ENotOwner);
        let entry_id = book.next_entry_id;
        book.next_entry_id = entry_id + 1;
        let entry = MemoryEntry {
            label,
            relationship,
            walrus_blob_id,
            last_interaction_unix_ms,
            notes_hash,
        };
        table::add(&mut book.entries, entry_id, entry);
        entry_id
    }

    /// Update an existing entry by ID.
    public entry fun update_entry(
        book: &mut MemoryBook,
        entry_id: u64,
        label: String,
        relationship: String,
        walrus_blob_id: String,
        last_interaction_unix_ms: u64,
        notes_hash: vector<u8>,
        ctx: &mut TxContext,
    ) {
        let sender = tx_context::sender(ctx);
        assert!(sender == book.owner, ENotOwner);
        if (!table::contains(&book.entries, entry_id)) {
            abort EEntryNotFound;
        };
        let entry = table::borrow_mut(&mut book.entries, entry_id);
        entry.label = label;
        entry.relationship = relationship;
        entry.walrus_blob_id = walrus_blob_id;
        entry.last_interaction_unix_ms = last_interaction_unix_ms;
        entry.notes_hash = notes_hash;
    }

    /// Borrow an entry by ID. Aborts if not found.
    public fun borrow_entry(book: &MemoryBook, entry_id: u64): &MemoryEntry {
        table::borrow(&book.entries, entry_id)
    }
}

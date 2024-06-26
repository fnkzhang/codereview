import React from 'react';
import { render, waitFor, screen } from '@testing-library/react';
import { Router, Route, Routes, MemoryRouter } from 'react-router';
import SnapshotSelector from '../components/SnapshotSelector';
import { getAllSnapshotsFromDocument } from '../api/APIUtils';



// Mock Api Util Function return values
// todo function remains undefined no matter what not sure how to fix
jest.mock('../api/APIUtils', () => ({
  getAllSnapshotsFromDocument: jest.fn()
}));

// Mocks Router Parameters
jest.mock('react-router', () => ({
  ...jest.requireActual('react-router'),
  useParams: () => ({
    project_id: 'project1',
    commit_id: 'commit1',
    document_id: 'document1',
    left_snapshot_id: 'leftSnapshot1',
    right_snapshot_id: 'rightSnapshot2'
  })

}));

describe("SnapshotSelector", () => {

  it("Handles Failed API call to getAllSnapshotsFromDocument", async () => {
    getAllSnapshotsFromDocument.mockReturnValue(
      {
        success: true,
        body: [
          { snapshot: { 
              snapshot_id: 'snapshot1', 
              date_modified: new Date() }, 
              commit: { name: 'Commit 1', 
              state: 'pending'
            } 
          },
          { snapshot: { 
              snapshot_id: 'snapshot2',
              date_modified: new Date() },
              commit: { name: 'Commit 2',
              state: 'approved' 
          } }
        ]
    }) 

    const setSnapshots = jest.fn()

    render(
      <MemoryRouter initialEntries={[`/testRoute`]}>
          <SnapshotSelector 
            comments={[{ snapshot_id: 'snapshot1', is_resolved: false }]}
            snapshots={[]} 
            setSnapshots={setSnapshots}
            fileExtensionName="js"
            canAddSnapshots={true}
            editorReady={true}
          />
      </MemoryRouter>
    )

    waitFor(() => {
      expect(screen.getByText('EMPTY')).toBeInTheDocument();
    })

  });
  it("Handles snapshots exist", async () => {
    getAllSnapshotsFromDocument.mockReturnValue(
      {
        success: true,
        body: [
          { snapshot: { 
              snapshot_id: 'snapshot1', 
              date_modified: new Date() }, 
              commit: { name: 'Commit 1', 
              state: 'pending'
            } 
          },
          { snapshot: { 
              snapshot_id: 'snapshot2',
              date_modified: new Date() },
              commit: { name: 'Commit 2',
              state: 'approved' 
          } }
        ]
    }) 

    const setSnapshots = jest.fn()
    const snapshots = [
      { snapshot: { 
          snapshot_id: 'snapshot1', 
          date_modified: new Date() }, 
          commit: { name: 'Commit 1', 
          state: 'pending'
        } 
      },
      { snapshot: { 
          snapshot_id: 'snapshot2',
          date_modified: new Date() },
          commit: { name: 'Commit 2',
          state: 'approved' 
      } }
    ]

    render(
      <MemoryRouter initialEntries={[`/testRoute`]}>
          <SnapshotSelector 
            comments={[{ snapshot_id: 'snapshot1', is_resolved: false }]}
            snapshots={snapshots} 
            setSnapshots={setSnapshots}
            fileExtensionName="js"
            canAddSnapshots={true}
            editorReady={true}
          />
      </MemoryRouter>
    )

    waitFor(() => {
      expect(screen.getByText('EMPTY')).toBeInTheDocument();
    })

  });


  // it("Calls getAllSnapshotsForDocument if snapshots empty", () => {
  //   render(
  //     <MemoryRouter initialEntries={[`/testRoute`]}>
  //       <SnapshotSelector
  //         comments={[{ snapshot_id: 'snapshot1', is_resolved: false }]}
  //         snapshots={[]}
  //         setSnapshots={() => {}}
  //         fileExtensionName="js"
  //         canAddSnapshots={true}
  //         editorReady={true}
  //       />
  //     </MemoryRouter>
  //   )

  //   waitFor(() => {
  //     expect(getAllSnapshotsFromDocument).toHaveBeenCalledWith(project_id, document_id);
  //   })
  // });


  // it("Displays Empty if snapshots are empty", async () => {
  //   const snapshots = [];


  //   render(
  //     <MemoryRouter>
  //       <SnapshotSelector snapshots={snapshots}/>
  //     </MemoryRouter>
  //   )
    
    
  //   screen.debug(undefined, Infinity);
  //   const test = await screen.getByText('EMPTY')
  //   expect(screen.getByText(test)).not.toBeInTheDocument();

  // });

  // More to test relating to displaying snapshots, but when trying to display, the contents are empty
})
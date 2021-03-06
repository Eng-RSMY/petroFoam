/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011-2013 OpenFOAM Foundation
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Application
    scalarTransportFoam

Description
    Solves a transport equation for a passive scalar

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "fvIOoptionList.H"
#include "faceSet.H"
#include "primitiveMesh.H"
#include "primitiveMeshTools.H"
#include "cellSet.H"


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //


int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    #include "createFields.H"
    #include "createFvOptions.H"
	
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

	while (runTime.run())
    {
		runTime++;
		

	    const vectorField& fAreas = mesh.faceAreas();
	    const vectorField& fCentres = mesh.faceCentres();
		const vectorField& cCentres = mesh.cellCentres();
		const primitiveMesh& meshh = mesh;
        const pointField& points = mesh.points();

        // Start of non orthogonality calculation
		tmp<scalarField> tortho = primitiveMeshTools::faceOrthogonality
		(
		    meshh,
		    fAreas,
		    cCentres
		);

		scalarField ortho = tortho();
		scalarField orthogonality = ortho;
		
		forAll(ortho, faceI)
		{
			if (ortho[faceI] > 1)
			{
				ortho[faceI] = 1;
			}
			else if (ortho[faceI] < -1)
			{
				ortho[faceI] = -1;
			}
		
			orthogonality[faceI] = radToDeg(::acos(ortho[faceI]));
		}

		forAll(orthogonality, faceI)
		{
			label cellI = mesh.faceOwner()[faceI];
			
			if (orthogonality[faceI] > nonOrth[cellI])
			{
				nonOrth[cellI] = orthogonality[faceI];
			}
		}

        //Write high non-orthogonal face-cells in the cellSet
        cellSet nonOrthCells(mesh, "nonOrthCells", mesh.nCells()/100);

        //Insert illegal cells in set
        forAll(nonOrth, cellI)
        {
            if(nonOrth[cellI] > 70)
            {
                nonOrthCells.insert(cellI);
            }
        }



        // Start of skewness calculation
        tmp<scalarField> tFaceSkew = primitiveMeshTools::faceSkewness
        (
            meshh,
            points,
            fCentres,
            fAreas,
            cCentres
        );

        scalarField faceSkew = tFaceSkew();

		forAll(faceSkew, faceI)
		{
			label cellI = mesh.faceOwner()[faceI];
			
			if (faceSkew[faceI] > skew[cellI])
			{
				skew[cellI] = faceSkew[faceI];
			}
		}

        //Write high skewed face-cells in the cellSet
        cellSet skewedCells(mesh, "skewedCells", mesh.nCells()/100);

        //Insert illegal cells in set
        forAll(skew, cellI)
        {
            if(skew[cellI] > 4)
            {
                skewedCells.insert(cellI);
            }
        }

        //Write cell sets
        nonOrthCells.write();
        skewedCells.write();
			
		runTime.write();
			
		Info<< "ExecutionTime = " << runTime.elapsedCpuTime() << " s"
		        << "  ClockTime = " << runTime.elapsedClockTime() << " s"
		        << nl << endl;
    }

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
